

import gzip
import numpy as np
import requests
import re
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render

import omero
from omeroweb.decorators import login_required
from omero.rtypes import unwrap
from omeroweb.webgateway.views import render_thumbnail

MDV_APP = "https://mdv-dev.netlify.app/"

# if running app from local vite.js dev server
# MDV_APP = "http://localhost:5173/"  # "http://10.201.197.162:5173/"


@login_required()
def index(request, conn=None, **kwargs):

    # get dataset etc...
    obj_id = None
    obj_type = None
    for dtype in ["dataset", "project"]:
        obj_id = request.GET.get(dtype)
        if obj_id:
            obj_type = dtype
            break
    if obj_id is None:
        return HttpResponse("Welcome to OMERO-MDV! - Use ?project=1 or ?dataset=1 to open.")

    obj = conn.getObject(dtype, obj_id)
    if obj is None:
        raise Http404(f"Couldn't find {dtype}: {obj_id}")

    # get annotations...\
    anns = []
    for ann in obj.listAnnotations():
        print("ann", ann, ann.ns)
        if hasattr(ann, "file"):
            f = ann.file
            print(f.mimetype.val, f.name.val)
            anns.append({
                "id": ann.id,
                "file": {
                    "id": f.id.val,
                    "name": f.name.val,
                    "mimetype": unwrap(f.mimetype)
                }
            })

    return render(request, "omero_mdv/index.html", {"anns": anns})


@login_required()
def submit_form(request, conn=None, **kwargs):

    # Handle form data from index page 

    # redirect to mdv_viewer?dir=config/ANN_ID/

    file_id = request.POST.get("file")
    print("file_id", file_id)

    url = reverse("mdv_urls", kwargs={"url": ""})
    config_url = "config/" + file_id + "/"

    # redirect to app, with absolute config URL...
    # Fails due to app at https not loading from dev omero-web (http)
    # url = MDV_APP
    # config_url = request.build_absolute_uri(reverse("mdv_urls", args=["config"]))
    # config_url = config_url + file_id + "/"

    return HttpResponseRedirect("%s?dir=%s" % (url, config_url))


def mdv_urls(request, url):

    print("url", repr(url))

    target_url = MDV_APP + url

    response = requests.get(target_url)
    content = response.content

    if len(url) == 0:
        # update links in html doc
        base_url = reverse("mdv_urls", kwargs={"url": ""})
        link_with_prefix = f'="{base_url}/assets/'
        content = content.replace(b'="/assets/', bytearray(link_with_prefix, 'utf-8'))

    rsp = HttpResponse(content)

    # headers to allow SharedArrayBuffer
    rsp["Cross-Origin-Opener-Policy"] = "same-origin"
    rsp["Cross-Origin-Embedder-Policy"] = "require-corp"

    if url.endswith(".js"):
        rsp['content-type'] = "application/javascript"

    return rsp


@login_required()
def state(request, tableid, conn=None, **kwargs):
    # only offer a single view initially...
    st = {
        "all_views":[
            "main",
        ],
        "initial_view": "main"
    }
    return JsonResponse(st)


@login_required()
def table_cols_byte_offsets(request, tableid, conn=None, **kwargs):
    # For each column, we need to get the number of bytes for the column
    # For now, we convert column into bytes and get size...

    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    col_byte_offsets = {}
    offset = 0

    try:
        cols = t.getHeaders()
        for column_index, col in enumerate(cols):
            column_name = col.name

            col_bytes = get_column_bytes(t, column_index)
            bytes_length = len(col_bytes)

            col_byte_offsets[column_name] = [offset, offset + bytes_length - 1]
            offset = offset + bytes_length
    finally:
        t.close()

    return JsonResponse(col_byte_offsets)


def get_column_bytes(table, column_index):

    print('get_column_bytes', column_index)
    row_count = table.getNumberOfRows()
    col_indices = [column_index]
    hits = range(row_count)
    res = table.slice(col_indices, hits)
    values = res.columns[0].values
    print('values', values, type(values[0]))
    dt = np.dtype(type(values[0]))
    if dt == np.int64:
        print("BYTES change")
        dt = np.int64
    print('dt', dt)
    arr = np.array(values)

    print(arr, arr.size, repr(arr[0]) )
    comp = gzip.compress(arr.tobytes())

    return comp


@login_required()
def table_bytes(request, tableid, conn=None, **kwargs):

    print("headers", request.headers)
    range_header = request.headers['Range']

    print('range_header', range_header)

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]:
        byte1 = int(g[0])
    if g[1]:
        byte2 = int(g[1])

    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    offset = 0

    size = 100000  # FIXME!
    column_bytes = b""
    # length = 0
    try:
        # We have to go though each column until we reach the offset
        cols = t.getHeaders()
        for column_index, col in enumerate(cols):
            column_name = col.name

            col_bytes = get_column_bytes(t, column_index)
            bytes_length = len(col_bytes)

            if offset == byte1:
                column_bytes = col_bytes
                break
            else:
                offset = offset + bytes_length
    finally:
        t.close()

    rsp = HttpResponse(column_bytes, content_type="application/octet-stream")
    rsp['Content-Range'] = 'bytes {0}-{1}/{2}'.format(byte1, byte2, size)
    rsp['Accept-Ranges'] = 'bytes'

    # headers to allow SharedArrayBuffer
    rsp["Cross-Origin-Opener-Policy"] = "same-origin"
    rsp["Cross-Origin-Embedder-Policy"] = "require-corp"
    return rsp

# def get_range(file_name,range_header):
#     file =open(file_name,"rb")
#     size = sys.getsizeof(file_name)
#     byte1, byte2 = 0, None

#     

#     file.seek(byte1)
#     data = file.read(length)
#     rv = Response(data,
#                 206,
#                 mimetype=mimetypes.guess_type(file_name)[0],
#                 direct_passthrough=True)
#     rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
#     rv.headers.add('Accept-Ranges', 'bytes')
#     file.close()
#     return rv

@login_required()
def views(request, tableid, conn=None, **kwargs):

    print('views', tableid)

    # only offer a single view initially...
    views = []

    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    image_col = None
    try:
        cols = t.getHeaders()
        column_names = [col.name for col in cols]
        number_cols = [col for col in cols if col.__class__.__name__ in ("LongColumn", "DoubleColumn")]
        for col in cols:
            if col.__class__.__name__ == "ImageColumn":
                image_col = col
    finally:
        t.close()

    pos_x = 0
    pos_y = 0
    chart_width = 300
    chart_height = 500
    gap = 10

    col_widths = {}

    for name in column_names:
        col_widths[name] = len(name) * 10

    # lets add a table...
    # views.append({
    #     "title": "Table",
    #     "legend": "Some table data",
    #     "type": "table_chart",
    #     "param": column_names,
    #     "id": "table_chart_%s" % tableid,
    #     "size": [
    #         chart_width,
    #         chart_height
    #     ],
    #     "column_widths": col_widths,
    #     "position": [
    #         pos_x,
    #         pos_y
    #     ]
    # })
    # pos_x = pos_x + chart_width + gap


    # If we have multiple number columns, add Scatter Plot...
    # if len(number_cols) > 1:
    #     views.append({
    #         "type":"wgl_scatter_plot",
    #         "title":"Scatter Plot",
    #         "param":[
    #             number_cols[0].name,
    #             number_cols[1].name
    #         ],
    #         "size": [
    #             chart_width,
    #             chart_height
    #         ],
    #         "position": [
    #             pos_x,
    #             pos_y
    #         ]
    #     })
    #     pos_x = pos_x + chart_width + gap


    if image_col:
        views.append({
            # Thumbnails to show filtered images
            "title": "Thumbnails",
            "legend": "",
            "type": "image_table_chart",
            "param": [image_col.name],
            "images": {
                "base_url": "./images/",
                "type": "png"
            },
            "id": "6qxshC",
            "size": [
                chart_width,
                chart_height
            ],
            "image_width": 96,
            "position": [
                pos_x,
                pos_y
            ]
        })
        pos_x = pos_x + chart_width + gap

    vw = {
        "main": {
            "initialCharts": {
                "OMERO.table_%s" % tableid: views
            }
        }
    }

                
    #             {
    #                 # Filter is for categories (string columns)
    #                 "title": "Filter",
    #                 "legend": "",
    #                 "type": "selection_dialog",
    #                 "param": [
    #                     "GO biological process",
    #                     "GO molecular function",
    #                     "GO cellular component"
    #                 ],
    #                 "id": "NDdxNC",
    #                 "size": [283, 375],
    #                 "filters": {
    #                     "GO biological process": {
    #                     "operand": "or",
    #                     "category": [],
    #                     "exclude": False
    #                     },
    #                     "GO cellular component": {
    #                     "operand": "or",
    #                     "category": [],
    #                     "exclude": False
    #                     },
    #                     "GO molecular function": {
    #                     "operand": "or",
    #                     "category": [],
    #                     "exclude": False
    #                     }
    #                 },
    #                 "position": [10, 10]
    #             },
    #             {
    #                 # Show a summary of the selected table row
    #                 "title": "Summary",
    #                 "legend": "",
    #                 "type": "row_summary_box",
    #                 "param": [
    #                     "Collection",
    #                     "Compartment",
    #                     "FlyBase link",
    #                     "OMEROFigurelink",
    #                     "figure_id"
    #                 ],
    #                 "image": {
    #                     "base_url": "./thumbnails/",
    #                     "type": "jpg",
    #                     "param": 4
    #                 },
    #                 "id": "XulQsf",
    #                 "size": [359, 574],
    #                 "position": [306, 4]
    #             },
    #             {
    #                 # Thumbnails to show filtered images
    #                 "title": "Thumbnails",
    #                 "legend": "",
    #                 "type": "image_table_chart",
    #                 "param": ["figure_id"],
    #                 "images": {
    #                     "base_url": "./images/",
    #                     "type": "png"
    #                 },
    #                 "id": "6qxshC",
    #                 "size": [599, 672],
    #                 "image_width": 146.07,
    #                 "position": [1068, 0]
    #             },
    #             {
    #                 # Histogram of Category column
    #                 "title": "GO cellular component",
    #                 "legend": "",
    #                 "type": "row_chart",
    #                 "param": "GO cellular component",
    #                 "id": "vIQ7Pg",
    #                 "size": [372, 675],
    #                 "axis": {
    #                     "x": {
    #                     "textSize": 13,
    #                     "label": "",
    #                     "size": 25,
    #                     "tickfont": 10
    #                     }
    #                 },
    #                 "show_limit": 40,
    #                 "sort": "size",
    #                 "position": [685, 0]
    #             }
    #         ]
    #         }
    #     }
    # }
    return JsonResponse(vw)


@login_required()
def datasources(request, tableid, conn=None, **kwargs):

    print('datasources', tableid)

    # open table and get columns...
    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    try:
        cols = t.getHeaders()
        row_count = t.getNumberOfRows()
    finally:
        t.close()

    cols_data = []

    col_types = {
        "ImageColumn": "integer",
        "WellColumn": "integer",
        "StringColumn": "text",
        "LongColumn": "integer",
        "DoubleColumn": "double"
    }

    for col in cols:
        print("col", col)
        colclass = col.__class__.__name__
        print("class", colclass)
        col_data = {
            "datatype": col_types[colclass],
            "name": col.name,   # display name
            "field": col.name,  # col name
            # "is_url": True,
        }

        # for 'text' columns, we want to get all the values
        #    "values": ["A", "B", "C"]
        # for integer & double, we want 
        #     "minMax": [2125613, 2147448],
        #     "quantiles": {
        #         "0.001": [2129988.88, 2147415.64],
        #         "0.01": [2137765.6, 2144999.6000000006],
        #         "0.05": [2137823, 2140299]
        #     }
        # }

        cols_data.append(col_data)

    ds = [
        {
            # This name will generate URL to load values
            "name": "OMERO.table_%s" % tableid,
            "size": row_count,
            "images": {
            "composites": {
                "base_url": "./images/",
                "type": "png",
                "key_column": "Image"
            }
            },
            "large_images": {
            "composites": {
                "base_url": "./images/",
                "type": "png",
                "key_column": "Image"
            }
            },
            "columns": cols_data
        }
    ]
    return JsonResponse(ds, safe=False)


@login_required()
def image(request, imageid, conn=None, **kwargs):

    return render_thumbnail(request, 59, conn=conn)
