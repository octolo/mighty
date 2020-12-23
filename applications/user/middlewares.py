from django.utils.deprecation import MiddlewareMixin
from mighty.functions import requet_kept
import uuid

class AnonymousMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        If user is not authenticated (anonymous) we set session hashcode
        uuid4 hex
        """
        if not request.user.is_authenticated and 'hashnonymous' not in request.session:
            request.session['hashnonymous'] = uuid.uuid4().hex

class RequestKeptMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        requet_kept.request = request
        return self.get_response(request)

    def process_exception(self, request, exception):
        requet_kept.request = None

    def process_template_response(self, request, response):
        requet_kept.request = None
        return response