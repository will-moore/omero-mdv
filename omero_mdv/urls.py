
from . import views
from django.urls import re_path

urlpatterns = [

    # MDV app viewer page
    re_path(r'^$', views.index, name='mdv_index'),

    # Open with MDV... opens the choose_data page with form -> submit_form
    re_path(r'^choose_data/$', views.choose_data, name='mdv_choose_data'),
    re_path(r'^submit_form/$', views.submit_form, name='mdv_submit_form'),

    # page above loads table info via...
    # re_path(r'^table_info/(?P<tableid>[0-9]+)/$', views.table_info, name='mdv_table_info'),
    # load map-annotations as if a table...
    re_path(r'^mapann_info/(?P<projectid>[0-9]+)/$', views.mapann_info, name='mdv_mapann_info'),

    # MDV viewer
    re_path(r"^config/(?P<configid>[0-9]+)/json/$", views.config_json, name='mdv_config_json'),
    # save configs, so a config ID is the FileAnnotation ID for JSON
    re_path(r"^config/(?P<configid>[0-9]+)/datasources.json$", views.datasources, name='mdv_datasources'),
    # list configs
    re_path(r'^config/$', views.list_mdv_configs),
    
    re_path(r"^config/(?P<tableid>[0-9]+)/state.json$", views.state, name='mdv_state'),
    re_path(r"^config/(?P<configid>[0-9]+)/views.json$", views.views, name='mdv_views'),

    # We name a table datasource mdv_config_ID, so we use that ID (ignore configid for now)
    re_path(r"^config/(?P<configid>[0-9]+)/mdv_config_(?P<tableid>[0-9]+).json$", views.table_cols_byte_offsets),
    re_path(r"^config/(?P<configid>[0-9]+)/mdv_config_(?P<tableid>[0-9]+).b$", views.table_bytes),

    re_path(r"^config/(?P<configid>[0-9]+)/thumbnail/(?P<imageid>[0-9]+).png$", views.thumbnail),
    re_path(r"^config/(?P<configid>[0-9]+)/image/(?P<imageid>[0-9]+).png$", views.image),

    re_path(r"^meths/execute_project_action/$", views.save_view),

    # Delegate all other requests from the viewer to statically-hosted files
    re_path(r'^(?P<url>.*)$', views.mdv_static, name='mdv_static'),
]
