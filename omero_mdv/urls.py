
from . import views
from django.urls import re_path

urlpatterns = [

    # index 'home page' of the MDV app
    re_path(r'^$', views.index, name='mdv_index'),
]
