
from collections import defaultdict

from django.http import Http404
import numpy as np
import gzip

import omero
from omero.rtypes import wrap, rlong

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
    
    return {'columns': cols_data, 'row_count': row_count}


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
