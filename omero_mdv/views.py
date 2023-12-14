
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
    get_text_indices, get_column_bytes, datasets_to_mdv_columns, mapanns_to_mdv_columns, update_file_ann, \
    save_text_to_file_annotation, get_column_values, get_random_id

JSON_FILEANN_NS = "omero.web.mdv_config.json"

WEBCLIENT_LINK = "webclient link"

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
    return JsonResponse({"columns": datasets_to_mdv_columns(conn, projectid)})


@login_required()
def mapanns_info(request, objtype, objid, conn=None, **kwargs):
    # for the 'choose_data' page, we don't load MDV formatted info...
    # return JsonResponse(_mapann_info(conn, projectid))

    if objtype != "project":
        raise Http404("Only 'project' supported just now")
    # ...instead load data in {'iid': {'key': 'values'}}
    return JsonResponse({"columns": mapanns_to_mdv_columns(conn, objid)})


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
    mdv_name = request.POST.get("mdv_name")
    # charts
    filters = request.POST.getlist("filter")
    rowcharts = request.POST.getlist("rowchart")
    histograms = request.POST.getlist("histogram")

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
                    t = r.openTable(omero.model.OriginalFileI(
                        table_id), conn.SERVICE_OPTS)
                    ids = get_column_values(t, column_index)
                    primary_keys["Image"] = ids
        group_id = conn.getObject(
            "OriginalFile", table_id).getDetails().group.id.val
        for idx, col in enumerate(tdata["columns"]):
            col["omero_table_file_id"] = table_id
            col["omero_table_column"] = idx
            # don't want to store OMERO.tables data in json
            if "data" in col:
                del(col["data"])

        columns.extend(tdata["columns"])
        # update bytes, needed for KVP etc below...
        bytes_offset = tdata["columns"][-1]["bytes"][1]

    # Handle KVPs and Datasets in the same way...
    for form_input in ["mapanns", "datasets"]:
        kvp_parent = request.POST.get(form_input)
        if kvp_parent is not None:
            # Load ALL Key-Value pairs in MDV format and save to config!!!!!!
            obj_id = int(kvp_parent.split("-")[1])
            # TODO: support other Object types instead of only 'project'
            if kvp_parent.startswith("project-"):
                if group_id is None:
                    group_id = conn.getObject(
                        "Project", obj_id).getDetails().group.id.val
                # Map-Anns and Datasets loaded in the same format...
                if form_input == "mapanns":
                    # if image_ids are None (no OMERO.table above), first column will be 'Image'
                    image_ids = primary_keys.get("Image")
                    cols = mapanns_to_mdv_columns(conn, obj_id, primary_keys=image_ids, bytes_offset=bytes_offset)
                    columns.extend(cols)
                    if image_ids is None:
                        primary_keys["Image"] = cols[0]["data"]
                    bytes_offset = cols[-1]["bytes"][1]
                else:
                    image_ids = primary_keys.get("Image")
                    cols = datasets_to_mdv_columns(conn, obj_id, primary_keys=image_ids, bytes_offset=bytes_offset)
                    columns.extend(cols)
                    if image_ids is None:
                        primary_keys["Image"] = cols[0]["data"]
                    bytes_offset = cols[-1]["bytes"][1]

    columns.append(get_webclient_links_column(primary_keys["Image"], bytes_offset))

    datasrcs = {
        "parent_type": "project",
        "columns": columns,
        "size": len(primary_keys["Image"]),
        "primary_keys": primary_keys,
    }
    if kvp_parent is not None:
        # E.g. project-1 - not used yet but might be useful to know
        datasrcs["parent_id"] = kvp_parent

    # Create initialView
    charts = []

    def get_column(name):
        return next(c for c in columns if c["name"] == name)

    # Filters
    if len(filters) > 0:
        fdata = {
            "title": "Filter Selection",
            "type": "selection_dialog",
            "param": filters,
            "id": get_random_id(),
            "filters": {},
        }
        for col_name in filters:
            col = get_column(col_name)
            filter_params = {}
            if col["datatype"] == "text":
                # start by NOT filtering anything
                filter_params["exclude"] = False
                filter_params["category"] = "__none__"
            elif col["datatype"] == "multitext":
                filter_params["operand"] = "or"
                filter_params["category"] = []
            else:
                # number filter - need min/max
                filter_params = col["minMax"]
            fdata["filters"][col_name] = filter_params
        charts.append(fdata)

    # Rowchart(s)
    for rowchart_name in rowcharts:
        col = get_column(rowchart_name)
        rcdata = {
          "title": rowchart_name,
          "legend": "",
          "type": "row_chart",
          "param": rowchart_name,
          "id": get_random_id(),
          "axis": {
            "x": {
              "textSize": 14,
              "label": "",
              "size": 30,
              "tickfont": 14
            }
          },
            #   "show_limit": len(col["values"]),  # show ALL values
          "sort": "size",
        }
        charts.append(rcdata)

    # Histogram (bar chart)
    for histogram_name in histograms:
        col = get_column(histogram_name)
        hdata = {
          "title": histogram_name,
          "legend": "",
          "type": "bar_chart",
          "param": histogram_name,
          "x": {
            "size": 30,
            "label": "my_double",
            "textsize": 13,
            "textSize": 13,
            "tickfont": 10
            },
          "y": {
            "size": 45,
            "label": "frequency",
            "textsize": 13,
            "textSize": 13,
            "tickfont": 10
          },
          "id": get_random_id(),
          "display_max": col["minMax"][1],
          "display_min": col["minMax"][0],
          # "bin_number": 10,
        }
        charts.append(hdata)


    charts = add_default_charts(datasrcs, charts)

    # single view "main" - we don't know THIS_DATASOURCE_ID yet...
    datasrcs["views"] = {"main": {
        "initialCharts": {
            "THIS_DATASOURCE_ID": charts,
        },
        "dataSources": {"THIS_DATASOURCE_ID": {"layout": "gridstack"}}
    }}

    config_json = json.dumps(datasrcs, indent=2)
    if group_id is None:
        return JsonResponse({"Error": "No data chosen"})
    conn.SERVICE_OPTS.setOmeroGroup(group_id)

    ann_id = save_text_to_file_annotation(
        conn, config_json, mdv_name, JSON_FILEANN_NS)

    # redirect to app, with absolute config URL...
    url = reverse("mdv_index")
    config_url = f"config/{ann_id}/"

    return HttpResponseRedirect("%s?dir=%s" % (url, config_url))


def get_webclient_links_column(image_ids, bytes_offset):

    indices = []
    values = []

    url = reverse("webindex")
    for index, iid in enumerate(image_ids):
        values.append(f"{url}?show=image-{iid}")
        indices.append(index)

    byte_count = len(get_column_bytes(indices))

    col = {
        "name": WEBCLIENT_LINK,
        "field": WEBCLIENT_LINK,
        "is_url": True,
        "datatype": "text",
        "values": values,
        "bytes": [bytes_offset, bytes_offset + byte_count],
        "data": indices,
    }
    return col


# we don't really need login here, but if not logged-in then
# loading other data will fail silently
@login_required()
def index(request, **kwargs):
    """ Main MDV viewer page """
    # home page of the mdv app - return index.html
    csrf_token = get_token(request)
    template = render_to_string("mdv/index.html", {}, request)
    template = template.replace(
        "</body>", "<script>window.CSRF_TOKEN='%s'</script></body>" % csrf_token)

    return HttpResponse(template)


# @require_POST
@login_required()
def save_view(request, conn=None, **kwargs):

    json_data = json.loads(request.body)

    # We want to find the "view"
    current_view = json_data["args"]["state"]["currentView"]
    view_json = json_data["args"]["state"]["view"]
    charts = view_json["initialCharts"]
    # need to use "mdv_config_ID" to find the config FileAnnotation
    for config_id, data in charts.items():
        ann_id = get_ann_id(config_id)
        # load FileAnnotation...
        config_json = _config_json(conn, ann_id)
        # we might not have "views" saved yet...
        if "views" not in config_json:
            config_json["views"] = {}

        config_json["views"][current_view] = view_json

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
    for col in config_json["columns"]:
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
        raise Http404(
            "No byte 'Range' in request Header: got `%s-%s`" % (byte1, byte2))
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


# def get_columns(mdv_config):
    # We combine the columns for each table in the config...
    # Making sure we avoid duplicate names/fields
    # columns = []
    # column_names = []

    # for col in mdv_config["columns"]:
        # colname = col["name"]
        # increment = 1
        # # avoid duplicate names - TODO: move this to submit()
        # while colname in column_names:
        #     colname = col["name"] + f"{len(column_names)}"
        #     increment += 1
        # col["name"] = colname
        # col["field"] = colname
        # column_names.append(col["name"])

        # We remove 'data' for map-ann/dataset columns, so it is lazily loaded as bytes
        # This requires the MDV project including data to be fully saved into JSON config
        # NB: if we *didn't* remove 'data' here, we'd need to encode it somehow for text/multitext?
        # if "data" in col:
        #     del (col["data"])
        # columns.append(col)

    # return columns


@login_required()
def views(request, configid, conn=None, **kwargs):

    # Load
    config_json = _config_json(conn, configid)

    # If views exist, simply return them...
    if "views" in config_json:
        rsp = {}
        for view_id, view_config in config_json["views"].items():
            # main, etc - charts is {datasource_id: []}
            initCharts = {}
            charts = view_config["initialCharts"]
            for datasourceId, ds_charts in charts.items():
                # If we saved this view before knowing the file ID we saved it to...
                if datasourceId == "THIS_DATASOURCE_ID":
                    datasourceId = charts_id(configid)
                initCharts[datasourceId] = ds_charts
            view_config["initialCharts"] = initCharts

            if "dataSources" in view_config:
                ds = {}
                for datasourceId, ds_info in view_config["dataSources"].items():
                    # If we saved this view before knowing the file ID we saved it to...
                    if datasourceId == "THIS_DATASOURCE_ID":
                        datasourceId = charts_id(configid)
                    ds[datasourceId] = ds_info
                view_config["dataSources"] = ds
            rsp[view_id] = view_config
        return JsonResponse(rsp)

    # create a default view...
    view_charts = add_default_charts(config_json)
    vw = {
        "main": {
            "initialCharts": {
                charts_id(configid): view_charts
            },
            "dataSources":{charts_id(configid):{"layout":"gridstack"}}
        }
    }
    return JsonResponse(vw)


def add_default_charts(config_json, charts=None, add_table=True,
                       add_thumbs=True, add_summary=True):

    if charts is None:
        charts = []
    column_names = []
    columns = config_json["columns"]
    # Don't add webclient-link column into Table
    column_names = [col["name"] for col in columns if col["name"] != WEBCLIENT_LINK]
    image_col = None
    for idx, col in enumerate(columns):
        if col["name"].lower() == "image":
            image_col = col
            image_col_index = idx

    # first, layout existing charts...
    grid_x = 0
    grid_y = 0

    chart_count = len(charts)

    # With the grid layout, we have 12 columns
    TOTAL_COLS = 12
    # do we save the right column for image panels?
    right_col_images = image_col is not None and (add_thumbs or add_summary)

    # most layouts divide the 12 grid into 4 (3 spaces per chart)
    chart_size_x = 3
    chart_size_y = 3
    available_cols = TOTAL_COLS

    # some layouts use bigger charts
    if right_col_images:
        available_cols = 9
        if chart_count < 3:
            chart_size_x = 4
            available_cols = 8
    else:
        if chart_count < 4:
            chart_size_x = 4


    # layout the existing charts into rows/columns
    for chart in charts:
        chart["gsposition"] = [grid_x, grid_y]
        chart["gssize"] = [chart_size_x, chart_size_y]
        grid_x += chart_size_x
        # if no room for next chart, start new row...
        if grid_x + chart_size_x > available_cols:
            grid_x = 0
            grid_y += chart_size_y

    # Always add a table below the charts, on a new row
    # using all available columns
    # if part-way through a row, start a new one...
    table_chart_size_x = available_cols - grid_x
    # if we had no charts, squeeze table into top-left
    if chart_count == 0 and right_col_images:
        table_chart_size_x = chart_size_x

    table_col_widths = {}
    for name in column_names:
        table_col_widths[name] = len(name) * 10
    charts.append({
        "title": "Table",
        "legend": "Some table data",
        "type": "table_chart",
        "param": column_names,
        "id": get_random_id(),
        "column_widths": table_col_widths,
        "gsposition": [
            grid_x,
            grid_y
        ],
        "gssize": [
            table_chart_size_x,
            chart_size_y
        ]
    })
    grid_x = grid_x + chart_size_x

    # thumbs and summary go in right column...
    grid_x = TOTAL_COLS - chart_size_x
    grid_y = 0
    
    # Thumbnails to show filtered images
    if right_col_images and add_thumbs:
        thumbs_chart_size_y = chart_size_y
        if chart_count < 2:
            # put thumbs in 2nd column
            grid_x = chart_size_x
        else:
            thumbs_chart_size_y = 2
        charts.append({
            "title": "Thumbnails",
            "legend": "",
            "type": "image_table_chart",
            "param": [image_col["name"]],
            "images": {
                "base_url": "./thumbnail/",
                "type": "png"
            },
            "id": get_random_id(),
            "image_width": 96,
            "gsposition": [
                grid_x,
                grid_y
            ],
            "gssize": [
                chart_size_x,
                thumbs_chart_size_y
            ]
        })
        if chart_count < 2:
            # side by side
            grid_x += chart_size_x
        else:
            grid_y += thumbs_chart_size_y

    # Show a summary - selected Image (if we have Images)
    if right_col_images and add_summary:
        charts.append({
            "title": "Summary",
            "legend": "",
            "type": "row_summary_box",
            "param": [image_col["name"], WEBCLIENT_LINK],
            "image": {
                "base_url": "./image/",
                "type": "png",
                "param": image_col_index
            },
            "id": get_random_id(),
            # "image_width": chart_width,
            "gsposition": [
                grid_x,
                grid_y
            ],
            "gssize": [
                chart_size_x,
                chart_size_y + 1,
            ]
        })
        grid_x = grid_x + chart_size_x

    return charts


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
    columns = config_json["columns"]
    # We remove 'data' for map-ann/dataset columns, so it is lazily loaded as bytes
    # This requires the MDV project including data to be fully saved into JSON config
    # NB: if we *didn't* remove 'data' here, we'd need to encode it somehow for text/multitext?
    for col in columns:
        if "data" in col:
            del (col["data"])

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
