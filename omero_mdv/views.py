
import re
import json
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from django.templatetags.static import static
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

import omero
from omeroweb.decorators import login_required
from omero.rtypes import unwrap, wrap
from omeroweb.webgateway.views import render_thumbnail, render_image

from django.conf import settings

from .utils import get_mapann_data, table_to_mdv_columns, list_file_anns, \
    get_text_indices, get_column_bytes, datasets_by_id, mapanns_by_id, update_file_ann, \
    save_text_to_file_annotation

JSON_FILEANN_NS = "omero.web.mdv_config.json"

# Ensure that middleware gets added
HEADERS_MIDDLEWARE = "omero_mdv.middleware.CrossOriginHeaders"
if HEADERS_MIDDLEWARE not in settings.MIDDLEWARE:
    settings.MIDDLEWARE = settings.MIDDLEWARE + (HEADERS_MIDDLEWARE,)

def charts_id(config_annid):
    return f"mdv_config_{config_annid}"

def get_ann_id(config_id):
    return int(config_id.replace("mdv_config_", ""))

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

    context = {
        "obj": {"id": obj_id, "type": obj_type, "name": obj.name},
        "anns": anns
    }
    return render(request, "mdv/choose_data.html", context)


@login_required()
def datasets_info(request, projectid, conn=None, **kwargs):
    # load data in {'iid': {'Dataset': 'name'}}
    return JsonResponse(datasets_by_id(conn, projectid))


@login_required()
def mapann_info(request, projectid, conn=None, **kwargs):
    # for the 'choose_data' page, we don't load MDV formatted info...
    # return JsonResponse(_mapann_info(conn, projectid))

    # ...instead load data in {'iid': {'key': 'values'}}
    return JsonResponse(mapanns_by_id(conn, projectid))


@login_required()
def list_mdv_configs(request, conn=None, **kwargs):

    context = {"configs": list_file_anns(conn, JSON_FILEANN_NS)}
    # return JsonResponse(context)
    return render(request, "mdv/configs.html", context)


def _mapann_info(conn, projectid):
    # summarise map-annotations to display in a table

    # dict of {'key': {iid: 'value'}}
    mapann_data = get_mapann_data(conn, projectid)

    # summary for columns
    # name and values for each column
    columns = []

    for col_name, id_vals in mapann_data.items():
        columns.append(
            {"name": col_name, "values": list(set(id_vals.values()))}
        )
    columns.sort(key=lambda col: col["name"])
    return {"columns": columns}


@login_required()
def table_info(request, tableid, conn=None, **kwargs):

    return JsonResponse(table_to_mdv_columns(conn, tableid))


@login_required()
def submit_form(request, conn=None, **kwargs):
    if not request.method == 'POST':
        return HttpResponse("Need to use POST")

    # Handle form data from index page 
    # redirect to mdv_viewer?dir=config/ANN_ID/

    file_ids = request.POST.getlist("file")
    kvp_parent = request.POST.get("map_anns")
    mdv_name = request.POST.get("mdv_name")

    # Load data to compile our MDV config file
    file_ids = [int(fid) for fid in file_ids]
    file_ids.sort()

    group_id = None
    datasrcs = {}
    if len(file_ids) > 0:
        datasrcs["omero_tables"] = []
    
    for table_id in file_ids:
        tdata = table_to_mdv_columns(conn, table_id)
        group_id = conn.getObject("OriginalFile", table_id).getDetails().group.id.val
        datasrcs["omero_tables"].append({
            "file_id": table_id,
            "columns": tdata["columns"]
        })

    if kvp_parent is not None:
        obj_id = int(kvp_parent.split("-")[1])
        # TODO: support other Object types
        if kvp_parent.startswith("project-"):
            if group_id is None:
                group_id = conn.getObject("Project", obj_id).getDetails().group.id.val
            mapann_data = _mapann_info(conn, obj_id)
            datasrcs["map_anns"] = {
                "parent_type": "project",
                "parent_id": obj_id,
                "columns": mapann_data["columns"]
            }

    config_json = json.dumps(datasrcs, indent=2)
    if group_id is None:
        return JsonResponse({"Error": "No data chosen"})
    conn.SERVICE_OPTS.setOmeroGroup(group_id)

    ann_id = save_text_to_file_annotation(conn, config_json, mdv_name, JSON_FILEANN_NS)

    # redirect to app, with absolute config URL...
    url = reverse("mdv_index")
    config_url = f"config/{ann_id}/"

    return HttpResponseRedirect("%s?dir=%s" % (url, config_url))


# we don't really need login here, but if not logged-in then
# loading other data will fail silently
@login_required()
def index(request, **kwargs):
    """ Main MDV viewer page """
    # home page of the mdv app - return index.html
    csrf_token = get_token(request)
    template = render_to_string("mdv/index.html", {}, request)
    template = template.replace("</body>", "<script>window.CSRF_TOKEN='%s'</script></body>" % csrf_token)

    return HttpResponse(template)


# @require_POST
@login_required()
def save_view(request, conn=None, **kwargs):

    json_data = json.loads(request.body)

    # We want to find the "view"
    current_view = json_data["args"]["state"]["currentView"]
    charts = json_data["args"]["state"]["view"]["initialCharts"]
    # need to use "mdv_config_ID" to find the config FileAnnotation
    for config_id, data in charts.items():
        ann_id = get_ann_id(config_id)
        # load FileAnnotation...
        config_json = _config_json(conn, ann_id)
        # we might not have "views" saved yet...
        if "views" not in config_json:
            config_json["views"] = {}

        config_json["views"][current_view] = charts

        config_txt = json.dumps(config_json, indent=2).encode('utf8')
        update_file_ann(conn, ann_id, config_txt)

    return JsonResponse({"success": True})


def mdv_static(request, url):
    """
    The MDV viewer requests all static files with relative URLs.
    
    So we need to redirect
    e.g 'assets/mdv.js' to `static/omero-mdv/assets/mdv.js`
    """
    url = static('mdv/' + url)
    return HttpResponseRedirect(url)


@login_required()
def state(request, configid, conn=None, **kwargs):

    config_json = _config_json(conn, configid)

    view_names = ["main"]

    if "views" in config_json:
        vjson = config_json["views"]
        view_names = list(vjson.keys())
    st = {
        "all_views": view_names,
        "initial_view": "main" if "main" in view_names else view_names[0],
        "permission": "edit"
    }
    return JsonResponse(st)


def _table_cols_byte_offsets(configid, conn, clear_cache=False):
    """Returns a dict of {'col_name': [start_byte, end_byte]}"""
    
    # Load
    config_json = _config_json(conn, configid)

    # {"col_name": [start, end]}
    col_byte_offsets = {}
    offset = 0

    # go through config to get bytes offsets for all columns
    # We combine the columns for each table in the config...
    for col in get_columns(config_json):
        column_name = col["name"]
        bytes_length = col["bytes"][1] - col["bytes"][0]
        col_byte_offsets[column_name] = [offset, offset + bytes_length - 1]
        offset = offset + bytes_length

    return col_byte_offsets


@login_required()
def table_cols_byte_offsets(request, configid, conn=None, **kwargs):
    clear_cache = request.GET.get('clear_cache') is not None
    return JsonResponse(_table_cols_byte_offsets(configid, conn, clear_cache))


@login_required()
def table_bytes(request, configid, conn=None, **kwargs):

    range_header = request.headers['Range']
    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    byte1 = int(g[0]) if g[0] else None
    byte2 = int(g[1]) if g[1] else None

    if byte1 is None or byte2 is None:
        raise Http404("No byte 'Range' in request Header: got `%s-%s`" % (byte1, byte2))
    size = byte2 - byte1

    # get data from config...
    config_json = _config_json(conn, configid)

    # need to find table_id and column index for requested bytes...
    offset = 0
    tableid = None
    column_index = 0
    # go through config to get bytes offsets for all columns
    # We combine the columns for each table in the config...
    for table_info in config_json["omero_tables"]:
        column_index = 0
        columns = table_info["columns"]
        for count, col in enumerate(columns):
            if offset == byte1:
                tableid = table_info["file_id"]
                column_index = count
                break
            bytes_length = col["bytes"][1] - col["bytes"][0]
            offset = offset + bytes_length
        if tableid is not None:
            break

    # TODO: THIS!
    # Add data from Map Anntations if we have some...
    # if "map_anns" in config_json:
    #     columns = config_json["map_anns"]["columns"]
    #     column_names.extend([col["name"] for col in columns])

    # get dict of {"col_name": [start, end]}
    # byte_offsets = _table_cols_byte_offsets(configid, conn)


    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    try:
        column_bytes = get_column_bytes(t, column_index)
    finally:
        t.close()

    rsp = HttpResponse(column_bytes, content_type="application/octet-stream")
    rsp['Content-Range'] = 'bytes {0}-{1}/{2}'.format(byte1, byte2, size)
    rsp['Accept-Ranges'] = 'bytes'
    return rsp


def get_columns(mdv_config):
    # We combine the columns for each table in the config...
    # Making sure we avoid duplicate names/fields
    columns = []
    column_names = []
    for table_info in mdv_config["omero_tables"]:
        for col in table_info["columns"]:
            colname = col["name"]
            increment= 1
            while colname in column_names:
                colname = col["name"] + f"{len(column_names)}"
                increment += 1
            col["name"] = colname
            col["field"] = colname
            columns.append(col)
            column_names.append(col["name"])
    
    # Add data from Map Anntations if we have some...
    # if "map_anns" in mdv_config:
    #     columns.extend(mdv_config["map_anns"]["columns"][:])

    return columns


@login_required()
def views(request, configid, conn=None, **kwargs):

    # Load
    config_json = _config_json(conn, configid)

    # If views exist, simply return them...
    if "views" in config_json:
        rsp = {}
        for view_id, charts in config_json["views"].items():
            # main, etc
            rsp[view_id] = {"initialCharts": charts}
        return JsonResponse(rsp)

    # ...otherwise generate an initial view from scratch...
    pos_x = 0
    pos_y = 0
    chart_width = 500
    chart_height = 500
    gap = 10

    views = []
    column_names = []

    columns = get_columns(config_json)
    column_names = [col["name"] for col in columns]
    image_col = None
    for idx, col in enumerate(columns):
        if col["name"].lower() == "image":
            image_col = col
            image_col_index = idx

    # lets add a table...
    col_widths = {}
    for name in column_names:
        col_widths[name] = len(name) * 10
    views.append({
        "title": "Table",
        "legend": "Some table data",
        "type": "table_chart",
        "param": column_names,
        "id": "table_chart_%s" % configid,
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
            "param": [image_col["name"]],
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
    if image_col:
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
                charts_id(configid): views
            }
        }
    }
    return JsonResponse(vw)


def _config_json(conn, fileid):
    file_ann = conn.getObject("FileAnnotation", fileid)
    if file_ann is None:
        raise Http404("File-Annotation %s not found" % fileid)
    mdv_json = b"".join(list(file_ann.getFileInChunks()))
    mdv_json = mdv_json.decode('utf8')
    # parse the json, so we can add info...
    config_json = json.loads(mdv_json)
    return config_json


@login_required()
def config_json(request, configid, conn=None, **kwargs):
    config_json = _config_json(conn, configid)
    return JsonResponse(config_json, safe=False)


@login_required()
def datasources(request, configid, conn=None, **kwargs):

    # Load
    config_json = _config_json(conn, configid)

    # We want to compile columns from all Tables, KVPs etc. 
    columns = []

    row_count = 1000

    columns = get_columns(config_json)

    ds = [
        {
            # This name will generate URL to load values
            "name": "mdv_config_%s" % configid,
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
            "columns": columns
        }
    ]
    return JsonResponse(ds, safe=False)


def table_datasources(request, tableid, conn=None, **kwargs):

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
                col_data["values"] = vals

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
