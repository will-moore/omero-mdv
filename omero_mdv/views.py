
import os
from django.http import HttpResponse

import mdv

def index(request):

    return HttpResponse("Welcome to OMERO-MDV!")


def static(request, filepath):

    mdv_path = os.path.dirname(mdv.__file__)
    print('mdv_path', mdv_path)

    static_path = os.path.join(mdv_path, "static/mdv", filepath)

    print('static_path', static_path)

    return HttpResponse(static_path
)