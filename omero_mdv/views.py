

import gzip
import numpy as np
import pandas as pd
import re
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from django.templatetags.static import static

import omero
from omeroweb.decorators import login_required
from omero.rtypes import unwrap
from omeroweb.webgateway.views import render_thumbnail, render_image

from django.conf import settings


# Ensure that middleware gets added
HEADERS_MIDDLEWARE = "omero_mdv.middleware.CrossOriginHeaders"
if HEADERS_MIDDLEWARE not in settings.MIDDLEWARE:
    settings.MIDDLEWARE = settings.MIDDLEWARE + (HEADERS_MIDDLEWARE,)


@login_required()
def choose_data(request, conn=None, **kwargs):

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

    obj = conn.getObject(obj_type, obj_id)
    if obj is None:
        raise Http404(f"Couldn't find {dtype}: {obj_id}")

    # get annotations...\
    anns = []
    for ann in obj.listAnnotations():
        if hasattr(ann, "file"):
            f = ann.file
            anns.append({
                "id": ann.id,
                "file": {
                    "id": f.id.val,
                    "name": f.name.val,
                    "mimetype": unwrap(f.mimetype)
                }
            })

    return render(request, "mdv/choose_data.html", {"anns": anns})


@login_required()
def submit_form(request, conn=None, **kwargs):

    # Handle form data from index page 
    # redirect to mdv_viewer?dir=config/ANN_ID/

    file_id = request.POST.get("file")

    url = reverse("mdv_index")
    config_url = "config/" + file_id + "/"

    # redirect to app, with absolute config URL...
    # Fails due to app at https not loading from dev omero-web (http)
    # url = MDV_APP
    # config_url = request.build_absolute_uri(reverse("mdv_urls", args=["config"]))
    # config_url = config_url + file_id + "/"

    return HttpResponseRedirect("%s?dir=%s" % (url, config_url))


# we don't really need login here, but if not logged-in then
# loading other data will fail silently
@login_required()
def index(request, **kwargs):
    """ Main MDV viewer page """
    # home page of the mdv app - return index.html
    rsp = render(request, "mdv/index.html", {})
    return rsp


def mdv_static(request, url):
    """
    The MDV viewer requests all static files with relative URLs.
    
    So we need to redirect
    e.g 'assets/mdv.js' to `static/omero-mdv/assets/mdv.js`
    """
    url = static('mdv/' + url)
    return HttpResponseRedirect(url)


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


def get_text_indices(values):
    unique_values = list(set(values))
    val_dict = {value: i for i, value in enumerate(unique_values)}
    return [val_dict[v] for v in values], [str(s) for s in unique_values]


def get_column_values(table, column_index):
    row_count = table.getNumberOfRows()
    col_indices = [column_index]
    hits = range(row_count)
    res = table.slice(col_indices, hits)
    return res.columns[0].values


def get_column_bytes(table, column_index):
    values = get_column_values(table, column_index)
    dt = np.dtype(type(values[0]))
    # if string, the values we want are indices
    if dt == str:
        indices, vals = get_text_indices(values)
        # Column 'text' type is OK for up to 256 values
        # TODO: support other column types
        # https://github.com/Taylor-CCB-Group/MDV/blob/main/docs/extradocs/datasource.md#datatype---text
        values = indices
        dt = np.int8
    else:
        dt = np.float32

    # MDV expects float32 encoding for numbers
    arr = np.array(values, dt)
    comp = gzip.compress(arr.tobytes())

    return comp


@login_required()
def table_bytes(request, tableid, conn=None, **kwargs):

    range_header = request.headers['Range']


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


    # only offer a single view initially...
    views = []

    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    image_col = None
    image_col_index = -1
    try:
        cols = t.getHeaders()
        column_names = [col.name for col in cols]
        number_cols = [col for col in cols if col.__class__.__name__ in ("LongColumn", "DoubleColumn")]
        for idx, col in enumerate(cols):
            if col.__class__.__name__ == "ImageColumn":
                image_col = col
                image_col_index = idx
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
    views.append({
        "title": "Table",
        "legend": "Some table data",
        "type": "table_chart",
        "param": column_names,
        "id": "table_chart_%s" % tableid,
        "size": [
            chart_width,
            chart_height
        ],
        "column_widths": col_widths,
        "position": [
            pos_x,
            pos_y
        ]
    })
    pos_x = pos_x + chart_width + gap


    # If we have multiple number columns, add Scatter Plot...
    if len(number_cols) > 1:
        views.append({
            "type":"wgl_scatter_plot",
            "title":"Scatter Plot",
            "param":[
                number_cols[0].name,
                number_cols[1].name
            ],
            "size": [
                chart_width,
                chart_height
            ],
            "position": [
                pos_x,
                pos_y
            ]
        })
        pos_x = pos_x + chart_width + gap


    if image_col:
        views.append({
            # Thumbnails to show filtered images
            "title": "Thumbnails",
            "legend": "",
            "type": "image_table_chart",
            "param": [image_col.name],
            "images": {
                "base_url": "./thumbnail/",
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

    # Show a summary - selected Image (if we have Images)
    views.append({
        "title": "Summary",
        "legend": "",
        "type": "row_summary_box",
        "param": column_names,
        "image": {
            "base_url": "./image/",
            "type": "png",
            "param": image_col_index
        },
        "id": "XulQsf",
         "size": [
            chart_width,
            chart_height
        ],
        "image_width": chart_width,
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
    return JsonResponse(vw)


@login_required()
def datasources(request, tableid, conn=None, **kwargs):


    # open table and get columns...
    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    try:
        cols = t.getHeaders()
        row_count = t.getNumberOfRows()

        cols_data = []

        col_types = {
            "ImageColumn": "integer",
            "WellColumn": "integer",
            "StringColumn": "text",
            "LongColumn": "integer",
            "DoubleColumn": "double"
        }

        for column_index, col in enumerate(cols):
            colclass = col.__class__.__name__
            col_data = {
                "datatype": col_types[colclass],
                "name": col.name,   # display name
                "field": col.name,  # col name
                # "is_url": True,
            }

            if col_data["datatype"] == "text":
                # we want to get all the values
                values = get_column_values(t, column_index)
                indices, vals = get_text_indices(values)
                print('indices, vals', indices, vals)
                col_data["values"] = vals

                # DEBUG: with this, we get the values (indices rendered correctly)
                # but without it, we get invalid text values
                # col_data["datatype"] = "integer"

            cols_data.append(col_data)
    finally:
        t.close()

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
def thumbnail(request, imageid, conn=None, **kwargs):
    return render_thumbnail(request, imageid, conn=conn)


@login_required()
def image(request, imageid, conn=None, **kwargs):
    return render_image(request, imageid, conn=conn)
