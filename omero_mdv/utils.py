
from io import BytesIO
from collections import defaultdict
from datetime import datetime
import time

from django.http import Http404
import numpy as np
import gzip

import omero
from omero.rtypes import wrap, rlong, unwrap

MDV_ANN_NAMESPACE = "omero-mdv.table_offsets"


def get_mdv_ann(conn, file_id):
    """Get the MDV table_offsets Annotation linked to File Annotation"""

    qs = conn.getQueryService()
    params = omero.sys.ParametersI()
    params.addId(file_id)

    query = ("select annLink from AnnotationAnnotationLink as annLink "
             "join fetch annLink.child as child "
             "join fetch annLink.parent as parent "
             "where parent.file.id=:id"
             )

    result = qs.findAllByQuery(query, params, conn.SERVICE_OPTS)

    if len(result) == 0:
        return None

    ann = result[0].child
    return {"id": ann.id.val, "textValue": ann.textValue.val}


def add_mdv_ann(conn, file_id, text):
    """Add Comment Annotation to File Annotation (specified by File ID)"""

    qs = conn.getQueryService()
    params = omero.sys.ParametersI()
    params.addId(file_id)

    query = ("select ann from FileAnnotation as ann "
             "where ann.file.id=:id"
             )

    result = qs.findAllByQuery(query, params, conn.SERVICE_OPTS)
    if len(result) == 0:
        raise AttributeError("No table found: %s" % file_id)

    file_ann = result[0]

    group_id = file_ann.details.group.id.val

    ctx = conn.SERVICE_OPTS.copy()
    ctx.setOmeroGroup(group_id)

    update = conn.getUpdateService()
    comment = omero.model.CommentAnnotationI()
    comment.textValue = wrap(text)
    comment.ns = wrap(MDV_ANN_NAMESPACE)
    comment = update.saveAndReturnObject(comment, ctx)

    # link
    link = omero.model.AnnotationAnnotationLinkI()
    link.parent = omero.model.FileAnnotationI(file_ann.id.val, False)
    link.child = comment
    link = update.saveAndReturnObject(link, ctx)

    return comment


def list_file_anns(conn, namespace):

    params = omero.sys.ParametersI()
    params.addString('ns', wrap(namespace))
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

    return rsp


def save_text_to_file_annotation(conn, text, filename, ns):
    # Save JSON to file annotation...
    update = conn.getUpdateService()
    text = text.encode('utf8')
    # Create new file
    file_size = len(text)
    f = BytesIO()
    f.write(text)
    orig_file = conn.createOriginalFileFromFileObj(
        f, '', filename, file_size, mimetype="application/json")
    # wrap it with File-Annotation to make it findable by NS etc.
    fa = omero.model.FileAnnotationI()
    fa.setFile(omero.model.OriginalFileI(orig_file.getId(), False))
    fa.setNs(wrap(ns))
    fa = update.saveAndReturnObject(fa, conn.SERVICE_OPTS)
    ann_id = fa.getId().getValue()
    return ann_id


def update_file_ann(conn, ann_id, text_contents, name=None, desc=None):
    # Update existing Original File
    fa = conn.getObject("FileAnnotation", ann_id)
    if fa is None:
        raise Http404("Couldn't find FileAnnotation of ID: %s" % ann_id)
    conn.SERVICE_OPTS.setOmeroGroup(fa.getDetails().group.id.val)
    update = conn.getUpdateService()
    # Update description
    if desc is not None:
        fa._obj.setDescription(wrap(desc))
    update.saveAndReturnObject(fa._obj, conn.SERVICE_OPTS)
    orig_file = fa._obj.file
    # Update name and size
    if name is not None:
        orig_file.setName(wrap(name))
    size = len(text_contents)
    orig_file.setSize(rlong(size))
    orig_file = update.saveAndReturnObject(
        orig_file, conn.SERVICE_OPTS)
    # upload file
    raw_file_store = conn.createRawFileStore()
    raw_file_store.setFileId(orig_file.getId().getValue(),
                             conn.SERVICE_OPTS)
    raw_file_store.write(text_contents, 0, size, conn.SERVICE_OPTS)
    raw_file_store.truncate(size, conn.SERVICE_OPTS)
    raw_file_store.save(conn.SERVICE_OPTS)
    raw_file_store.close()


def get_mapann_data(conn, projectid):
    """
    Get all MapAnnotations on Images in a Project

    Return dict of {'key': {iid: 'value'}}
    where each 'key' becomes a table column
    """
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


def table_to_mdv_columns(conn, tableid):

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

            values = get_column_values(t, column_index)
            if col_data["datatype"] == "text":
                # we want to get all the values...
                indices, vals = get_text_indices(values)
                # ...These are the unique values
                col_data["values"] = vals

            col_bytes = get_column_bytes(values)
            bytes_length = len(col_bytes)
            col_data['bytes'] = [offset, offset + bytes_length]
            offset = offset + bytes_length

            cols_data.append(col_data)
    finally:
        t.close()

    return {'columns': cols_data, 'row_count': row_count}


def datasets_by_id(conn, projectid):
    # load data in {'iid': {'Dataset Name': ['name', 'name2]}}
    # Same format as mapanns_by_id

    params = omero.sys.ParametersI()
    params.addId(projectid)
    qs = conn.getQueryService()
    q = """
        select image from Image as image
        left outer join fetch image.datasetLinks as dsl
        join fetch dsl.parent as dataset
        left outer join dataset.projectLinks as pl
        join pl.parent as project where project.id=:id
    """
    results = qs.findAllByQuery(q, params, conn.SERVICE_OPTS)
    rsp = defaultdict(lambda: defaultdict(list))
    for img in results:
        img_id = img.id.val
        for dsl in img.copyDatasetLinks():
            # List handles case of Image in 2 Datasets
            rsp[img_id]["Dataset_Name"].append(dsl.parent.name.val)
    return {"data": rsp, "keys": ["Dataset_Name"]}


def mapanns_by_id(conn, projectid):
    # load data in {'iid': {'key': ['value', 'value2']}}

    params = omero.sys.ParametersI()
    params.addId(projectid)
    qs = conn.getQueryService()
    q = """
        select image.id from Image as image
        left outer join image.datasetLinks as dsl
        join dsl.parent as dataset
        left outer join dataset.projectLinks as pl
        join pl.parent as project
        where project.id=:id
    """
    result = qs.projection(q, params, conn.SERVICE_OPTS)
    iids = [r[0].val for r in result]
    print("iids", iids)

    params = omero.sys.ParametersI()
    params.addIds(iids)
    q = """
        select oal from ImageAnnotationLink as oal
        left outer join fetch oal.child as ch
        left outer join fetch oal.parent as image
        where ch.class=MapAnnotation
        and image.id in (:ids)
    """
    results = qs.findAllByQuery(q, params, conn.SERVICE_OPTS)
    rsp = defaultdict(lambda: defaultdict(list))
    keys = set()
    for img_ann_link in results:
        img_id = img_ann_link.parent.id.val
        ann = img_ann_link.child
        for kv in ann.getMapValue():
            keys.add(kv.name)
            rsp[img_id][kv.name].append(kv.value)
    keys = list(keys)
    keys.sort()

    # make sure we include images without KVPs
    for iid in iids:
        if iid not in rsp:
            rsp[iid] = {}

    return {"data": rsp, "keys": keys}


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


def get_column_bytes(values, dt=None):
    if dt is None:
        first_dt = np.dtype(type(values[0]))
        # if string, the values we want are indices
        if first_dt == str:
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


def marshal_mdv_column(colname, kvp_by_id, primary_key_ids, bytes_offset):
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
    # columns is {"name": {"datatype": "integer|text|double"}}
    datatype = "integer"
    vals = list(vals)
    vals.sort()

    for val in vals:
        if datatype == "integer":
            try:
                int(val)
            except ValueError:
                datatype = "double"
        if datatype == "double":
            try:
                float(val)
            except ValueError:
                datatype = "text"

    # Now, for each row/image, convert KVP values into indicies
    kvp_data = []
    for iid in primary_key_ids:
        obj_kvp = kvp_by_id[iid]
        indices = []
        if datatype == "text":
            if colname in obj_kvp:
                obj_vals = obj_kvp[colname]
                indices = [vals.index(v) for v in obj_vals]
            for fill in range(max_value_count - len(indices)):
                indices.append(65535)
            kvp_data.extend(indices)
        else:
            # for number columns, we don't handle multiple Values for a Key...
            obj_vals = obj_kvp.get(colname, [MISSING_NUMBER])
            #...just pick first
            number_val = int(obj_vals[0]) if datatype == "integer" else float(obj_vals[0])
            kvp_data.append(number_val)

    byte_count = len(get_column_bytes(kvp_data))

    if datatype == "text" and max_value_count > 1:
        datatype == "multitext"
    col = {
        "name": colname,
        "datatype": datatype,
        "data": kvp_data,
        "bytes": [bytes_offset, bytes_offset + byte_count]
    }
    if "text" in datatype:
        col["values"] = vals
    if max_value_count > 1:
        col["stringLength"] = max_value_count

    return col
