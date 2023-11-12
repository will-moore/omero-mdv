
import re
import json
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from django.templatetags.static import static
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
import numpy as np

import omero
from omeroweb.decorators import login_required
from omero.rtypes import unwrap, wrap
from omeroweb.webgateway.views import render_thumbnail, render_image

from django.conf import settings

from .utils import get_mapann_data, table_to_mdv_columns, list_file_anns, \
    get_text_indices, get_column_bytes, datasets_by_id, mapanns_by_id, update_file_ann, \
    save_text_to_file_annotation, get_column_values

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
def mapanns_info(request, projectid, conn=None, **kwargs):
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
    kvp_parent = request.POST.get("mapanns")
    mdv_name = request.POST.get("mdv_name")

    # Load data to compile our MDV config file
    file_ids = [int(fid) for fid in file_ids]
    file_ids.sort()

    group_id = None

    # Look-up Image IDs as 'primary keys' and save these to the config
    primary_keys = {}

    bytes_offset = 0

    columns = []

    # TODO: support multiple tables *properly*
    # - upate bytes_offset in each table (don't start at 0 for all)
    # - need to *reorder* data by primary_keys - CHECK if this affects byte sizes?!
    for table_id in file_ids:
        tdata = table_to_mdv_columns(conn, table_id)
        # just use the *first* table to set primary keys...
        if "Image" not in primary_keys:
            for column_index, col in enumerate(tdata["columns"]):
                if col["name"] == "Image":
                    r = conn.getSharedResources()
                    t = r.openTable(omero.model.OriginalFileI(table_id), conn.SERVICE_OPTS)
                    ids = get_column_values(t, column_index)
                    primary_keys["Image"] = ids
        group_id = conn.getObject("OriginalFile", table_id).getDetails().group.id.val
        for idx, col in enumerate(tdata["columns"]):
            col["omero_table_file_id"] = table_id
            col["omero_table_column"] = idx

        columns.extend(tdata["columns"])
        # update bytes, needed for KVP etc below...
        bytes_offset = tdata["columns"][-1]["bytes"][1]

    if kvp_parent is not None:
        # Load ALL Key-Value pairs in MDV format and save to config!!!!!!
        obj_id = int(kvp_parent.split("-")[1])
        # TODO: support other Object types instead of only 'project'
        if kvp_parent.startswith("project-"):
            if group_id is None:
                group_id = conn.getObject("Project", obj_id).getDetails().group.id.val
            # This includes all KVP values, saved below...
            rsp = mapanns_by_id(conn, obj_id)
            kvp_by_id = rsp["data"]
            kvp_keys = rsp["keys"]

            # TODO: If we DO have primary keys,
            if "Image" not in primary_keys:
                iids = list(kvp_by_id.keys())
                iids.sort()
                primary_keys["Image"] = iids
                # Create an "Image" column
                img_bytes = get_column_bytes(iids)
                byte_count = len(img_bytes)
                columns.append({
                    "name": "Image",
                    "field": "Image",
                    "datatype": "integer",
                    "bytes": [bytes_offset, bytes_offset + byte_count],
                    "data": iids    # TODO: this is duplicate of 'primary_keys' - maybe don't need them now?
                })
                bytes_offset += byte_count

            for colname in kvp_keys:
                # create column with list of all known 'values' 
                # and the data is the index
                # https://github.com/Taylor-CCB-Group/MDV/blob/main/docs/extradocs/datasource.md#datatype--mulitext
                # [ "A,B,C", "B,A", "A,B", "D,E", "E,C,D" ]
                # would be converted to
                # values:["A","B","C","D","E"]
                # stringLength:3
                # data:[0,1,2, 1,0,65535, 0,1,65535, 3,4,65535, 0,2,3] //(Uint16Array)

                # first get ALL values for this key...
                vals = set()
                max_value_count = 0
                for key_vals in kvp_by_id.values():
                    # handle multiple values for a key
                    obj_vals = key_vals.get(colname, [])
                    max_value_count = max(max_value_count, len(obj_vals))
                    vals.update(obj_vals)

                # TODO: if all vals are Numbers, create an "integer" or "double" column!
                vals = list(vals)
                vals.sort()

                # Now, for each row/image, convert KVP values into indicies
                kvp_data = []
                for iid in primary_keys["Image"]:
                    obj_kvp = kvp_by_id[iid]
                    indices = []
                    if colname in obj_kvp:
                        obj_vals = obj_kvp[colname]
                        indices = [vals.index(v) for v in obj_vals]
                    for fill in range(max_value_count - len(indices)):
                        indices.append(65535)
                    kvp_data.extend(indices)

                byte_count = len(get_column_bytes(kvp_data))

                col = {
                    "name": colname,
                    "datatype": "text" if max_value_count == 1 else "multitext",
                    "values": vals,
                    "data": kvp_data,
                    "bytes": [bytes_offset, bytes_offset + byte_count]
                }
                if max_value_count > 1:
                    col["stringLength"] = max_value_count
                columns.append(col)
                bytes_offset += byte_count

    datasrcs = {
        "parent_type": "project",
        "columns": columns,
        "size": len(primary_keys["Image"]),
        "primary_keys": primary_keys,
    }
    if kvp_parent is not None:
        # E.g. project-1 - not used yet but might be useful to know
        datasrcs["parent_id"] = kvp_parent

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
    tableid = None
    column_index = 0
    column_bytes = None
    # find the column that has the correct byte1 (used as column ID)
    for col in config_json["columns"]:
        if col["bytes"][0] == byte1:
            # handle omero tables, load table below
            if "omero_table_file_id" in col:
                tableid = col.get("omero_table_file_id")
                column_index = col["omero_table_column"]
            elif "data" in col:
                dtype = None
                if col["datatype"] == "text":
                    dtype = np.int8
                elif col["datatype"] == "multitext":
                    dtype = np.int16
                column_bytes = get_column_bytes(col["data"], dtype)
            break

    if tableid is not None:
        r = conn.getSharedResources()
        t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
        if not t:
            raise Http404("Table %s not found" % tableid)
        try:
            values = get_column_values(t, column_index)
            column_bytes = get_column_bytes(values)
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

    for col in mdv_config["columns"]:
        colname = col["name"]
        increment= 1
        # avoid duplicate names - TODO: move this to submit()
        while colname in column_names:
            colname = col["name"] + f"{len(column_names)}"
            increment += 1
        col["name"] = colname
        col["field"] = colname
        column_names.append(col["name"])

        # remove 'data' for map-ann/dataset columns
        if "data" in col:
            del(col["data"])
        columns.append(col)

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
    columns = get_columns(config_json)

    # Single datasource since we join everything into one table
    ds = [
        {
            # This name will generate URL to load values
            "name": "mdv_config_%s" % configid,
            "size": config_json["size"],
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


@login_required()
def delete_mdv_config(request, conn=None, **kwargs):
    """ POST 'ann_id' to delete the FileAnnotation """

    if request.method != 'POST':
        return HttpResponse("Need to POST 'ann_id' to delete")

    ann_id = request.POST.get('ann_id')
    conn.deleteObjects("Annotation", [ann_id], wait=True)
    url = reverse("open_mdv")
    return HttpResponseRedirect(url)
