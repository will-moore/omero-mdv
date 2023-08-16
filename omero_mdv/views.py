

from collections import defaultdict
import gzip
from datetime import datetime
import time
from io import BytesIO
import numpy as np
import pandas as pd
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

from .utils import get_mdv_ann, add_mdv_ann

JSON_FILEANN_NS = "omero.web.mdv_config.json"

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

    context = {
        "obj": {"id": obj_id, "type": obj_type, "name": obj.name},
        "anns": anns
    }
    return render(request, "mdv/choose_data.html", context)


@login_required()
def mapann_info(request, projectid, conn=None, **kwargs):
    return JsonResponse(_mapann_info(conn, projectid))


@login_required()
def list_mdv_configs(request, conn=None, **kwargs):

    params = omero.sys.ParametersI()
    params.addString('ns', wrap(JSON_FILEANN_NS))
    q = """select new map(obj.id as id,
                obj.description as desc,
                o.id as owner_id,
                o.firstName as firstName,
                o.lastName as lastName,
                e.time as time,
                f.name as name,
                f.id as file_id,
                g.id as group_id,
                g.name as group_name,
                obj as obj_details_permissions)
            from FileAnnotation obj
            join obj.details.group as g
            join obj.details.owner as o
            join obj.details.creationEvent as e
            join obj.file.details as p
            join obj.file as f where obj.ns=:ns"""

    qs = conn.getQueryService()
    file_anns = qs.projection(q, params, conn.SERVICE_OPTS)
    rsp = []
    for file_ann in file_anns:
        fa = unwrap(file_ann[0])
        date = datetime.fromtimestamp(unwrap(fa['time'])/1000)
        first_name = unwrap(fa['firstName'])
        last_name = unwrap(fa['lastName'])
        fig_file = {
            'id': unwrap(fa['id']),
            'file': {
                'id': unwrap(fa['file_id']),
                'name': unwrap(fa['name']),
            },
            'description': unwrap(fa['desc']),
            'ownerFullName': "%s %s" % (first_name, last_name),
            'owner': {
                'id': fa['owner_id'],
                'firstName': fa['firstName'],
                'lastName': fa['lastName']
            },
            'group': {
                'id': fa['group_id'],
                'name': fa['group_name']
            },
            'creationDate': time.mktime(date.timetuple()),
            'formattedDate': str(date.strftime('%a %d %b %Y, %I:%M%p')),
            'canEdit': fa['obj_details_permissions'].get('canEdit')
        }
        rsp.append(fig_file)

    context = {"configs": rsp}
    # return JsonResponse(context)
    return render(request, "mdv/configs.html", context)


def _mapann_info(conn, projectid):
    # summarise map-annotations to display in a table

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


def get_mapann_data(conn, projectid):
    qs = conn.getQueryService()
    params = omero.sys.ParametersI()
    params.addId(projectid)

    query = """select ilink from ImageAnnotationLink as ilink
            left outer join fetch ilink.child as ch
            left outer join fetch ilink.parent as img
            left outer join fetch img.datasetLinks as dlink
            join fetch dlink.parent as dataset
            left outer join fetch dataset.projectLinks as plink
            join fetch plink.parent as project
            where project.id=:id
            and ch.class=MapAnnotation"""
    
    result = qs.findAllByQuery(query, params, conn.SERVICE_OPTS)

    # need {key: {iid: value} }
    kv_pairs = defaultdict(dict)
    for annLink in result:
        ann = annLink.child
        img = annLink.parent
        for kv in ann.mapValue:
            kv_pairs[kv.name][img.id.val] = kv.value
    return kv_pairs


@login_required()
def table_info(request, tableid, conn=None, **kwargs):
    return JsonResponse(_table_info(conn, tableid))


def _table_info(conn, tableid):
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

        offset = 0

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

            col_bytes = get_column_bytes(t, column_index)
            bytes_length = len(col_bytes)
            col_data['bytes'] = [offset, offset + bytes_length - 1]
            offset = offset + bytes_length

            cols_data.append(col_data)
    finally:
        t.close()
    
    return {'columns': cols_data, "row_count": row_count}


@login_required()
def submit_form(request, conn=None, **kwargs):
    if not request.method == 'POST':
        return HttpResponse("Need to use POST")

    # Handle form data from index page 
    # redirect to mdv_viewer?dir=config/ANN_ID/

    file_ids = request.POST.getlist("file")
    kvp_parent = request.POST.get("map_anns")
    mdv_name = request.POST.get("mdv_name")

    print("file_ids", file_ids, "kvp_parent", kvp_parent, "mdv_name", mdv_name)

    # Load data to compile our MDV config file
    file_ids = [int(fid) for fid in file_ids]
    file_ids.sort()

    group_id = None
    datasrcs = {}
    if len(file_ids) > 0:
        datasrcs["omero_tables"] = []
    
    for table_id in file_ids:
        tdata = _table_info(conn, table_id)
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

    if group_id is None:
        return JsonResponse({"Error": "No data chosen"})
    conn.SERVICE_OPTS.setOmeroGroup(group_id)
    config_json = json.dumps(datasrcs, indent=2)

    # Save JSON to file annotation...
    update = conn.getUpdateService()
    config_json = config_json.encode('utf8')
    # Create new file
    file_size = len(config_json)
    f = BytesIO()
    f.write(config_json)
    orig_file = conn.createOriginalFileFromFileObj(
        f, '', mdv_name, file_size, mimetype="application/json")
    # wrap it with File-Annotation to make it findable by NS etc.
    fa = omero.model.FileAnnotationI()
    fa.setFile(omero.model.OriginalFileI(orig_file.getId(), False))
    fa.setNs(wrap(JSON_FILEANN_NS))
    fa = update.saveAndReturnObject(fa, conn.SERVICE_OPTS)
    ann_id = fa.getId().getValue()

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
    # {% csrf_token %}
    csrf_token = get_token(request)
    print("csrf_token", csrf_token)
    template = render_to_string("mdv/index.html", {}, request)
    template = template.replace("</body>", "<script>window.CSRF_TOKEN='%s'</script></body>" % csrf_token)
    # rsp = render(request, , {"CSRF_TOKEN": csrf_token})

    return HttpResponse(template)


# @require_POST
@login_required()
def save_view(request, **kwargs):

    print("save view")

    try:
        json_data = json.loads(request.body)
        print("json_data", json.dumps(json_data))
    except Exception as ex:
        return JsonResponse({"success": False, "Error": ex.message})

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
def state(request, tableid, conn=None, **kwargs):
    # only offer a single view initially...
    st = {
        "all_views":[
            "main",
        ],
        "initial_view": "main",
        "permission": "edit"
    }
    return JsonResponse(st)


def _table_cols_byte_offsets(tableid, conn, clear_cache=False):
    """Returns a dict of {'col_name': [start_byte, end_byte]}"""

    # check for cached values as an Annotation
    ann = get_mdv_ann(conn, tableid)
    if ann is not None:
        if clear_cache:
            conn.deleteObjects("Annotation", [ann["id"]])
            return {"cache_cleared": "True"}
        else:
            return json.loads(ann["textValue"])

    # For each column, we need to get the number of bytes for the column
    # Convert each column into bytes and get size...
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

    # cache
    add_mdv_ann(conn, tableid, json.dumps(col_byte_offsets))

    return col_byte_offsets


@login_required()
def table_cols_byte_offsets(request, tableid, conn=None, **kwargs):
    clear_cache = request.GET.get('clear_cache') is not None
    return JsonResponse(_table_cols_byte_offsets(tableid, conn, clear_cache))


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

    # get dict of {"col_name": [start, end]}
    byte_offsets = _table_cols_byte_offsets(tableid, conn)

    range_header = request.headers['Range']

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    byte1 = int(g[0]) if g[0] else None
    byte2 = int(g[1]) if g[1] else None

    if byte1 is None or byte2 is None:
        raise Http404("No byte 'Range' in request Header: got `%s-%s`" % (byte1, byte2))
    size = byte2 - byte1

    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(tableid), conn.SERVICE_OPTS)
    if not t:
        raise Http404("Table %s not found" % tableid)

    try:
        # We have to go though each column until we reach the offset
        cols = t.getHeaders()
        for column_index, col in enumerate(cols):
            column_name = col.name
            start_end = byte_offsets.get(column_name)
            if start_end is not None and start_end[0] == byte1:
                column_bytes = get_column_bytes(t, column_index)
    finally:
        t.close()

    rsp = HttpResponse(column_bytes, content_type="application/octet-stream")
    rsp['Content-Range'] = 'bytes {0}-{1}/{2}'.format(byte1, byte2, size)
    rsp['Accept-Ranges'] = 'bytes'
    return rsp


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


def _config_json(conn, fileid):
    file_ann = conn.getObject("FileAnnotation", fileid)
    if file_ann is None:
        raise Http404("File-Annotation %s not found" % fileid)
    mdv_json = b"".join(list(file_ann.getFileInChunks()))
    mdv_json = mdv_json.decode('utf8')
    print("mdv_json", mdv_json)
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
    for table_json in config_json["omero_tables"]:
        columns.extend(table_json["columns"])

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
