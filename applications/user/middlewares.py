from django.utils.deprecation import MiddlewareMixin
import uuid

class AnonymousMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        If user is not authenticated (anonymous) we set session hashcode
        uuid4 hex
        """
        if not request.user.is_authenticated and 'hashcode' not in request.session:
            request.session['hashcode'] = uuid.uuid4().hex