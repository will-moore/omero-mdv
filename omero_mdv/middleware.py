
class CrossOriginHeaders:
    """ MDV needs these headings to allow SharedArrayBuffer"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Embedder-Policy"] = "require-corp"
        return response