
from django.http import Http404
MDV_ANN_NAMESPACE = "omero-mdv.table_offsets"

import omero
from omero.rtypes import wrap, rlong

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
