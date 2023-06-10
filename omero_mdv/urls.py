
from . import views
from django.urls import re_path

urlpatterns = [

    # index 'home page' of the MDV app
    re_path(r'^$', views.index, name='mdv_index'),

    re_path(r'^submit_form/$', views.submit_form, name='mdv_submit_form'),

    # MDV viewer
    # Currently we don't save configs, so a config ID is really an OMERO.table ID
    re_path(r"^mdv/config/(?P<tableid>[0-9]+)/datasources.json$", views.datasources, name='mdv_datasources'),
    re_path(r"^mdv/config/(?P<tableid>[0-9]+)/state.json$", views.state, name='mdv_state'),
    re_path(r"^mdv/config/(?P<tableid>[0-9]+)/views.json$", views.views, name='mdv_views'),

    # We name a table datasource OMERO.table_ID, so we use that ID (ignore configid for now)
    re_path(r"^mdv/config/(?P<configid>[0-9]+)/OMERO.table_(?P<tableid>[0-9]+).json$", views.table_cols_byte_offsets),
    re_path(r"^mdv/config/(?P<configid>[0-9]+)/OMERO.table_(?P<tableid>[0-9]+).b$", views.table_bytes),

    re_path(r"^mdv/config/(?P<configid>[0-9]+)/thumbnail/(?P<imageid>[0-9]+).png$", views.thumbnail),
    re_path(r"^mdv/config/(?P<configid>[0-9]+)/image/(?P<imageid>[0-9]+).png$", views.image),

    # MDV viewer itself is at /mdv/
    # Delegate all /mdv/... urls to statically-hosted files or json etc
    re_path(r'^mdv/(?P<url>.*)$', views.mdv_urls, name='mdv_urls'),
]
