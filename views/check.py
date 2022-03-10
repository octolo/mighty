from django.http import JsonResponse
from mighty.views.template import TemplateView
from mighty import translates as _
from mighty.functions import setting
from django.core.exceptions import MultipleObjectsReturned
# Check data side server
class CheckData(TemplateView):
    test_field = None
    model = None
    http_error = 400
    http_status = 200

    def get_request_type(self):
        if hasattr(self.request, "POST"):
            return self.request.POST
        return self.request.GET

    def get_data(self):
        return self.get_request_type().get('check', self.request.GET.get("check"))

    def get_queryset(self, queryset=None):
        return self.model.objects.get(**{self.test_field: self.get_data()})

    def msg_no_errors(self):
        return { "message": _.no_errors, "valid": True }

    def msg_errors(self, error):
        self.http_status = self.http_error
        return { "valid": False, "code": error.code, "msg": error.message }

    def check_alreay_exist(self):
        self.get_queryset()
        raise MultipleObjectsReturned()

    def check_data(self):
        try:
            self.check_already_exist()
        except self.model.DoesNotExist:        
            return self.msg_no_errors()
        except MultipleObjectsReturned as e:
            return self.msg_errors(e)

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.check_data(), 
            safe=False, status=self.http_status, **response_kwargs)

if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.views import APIView
    from rest_framework.response import Response
    
    class CheckData(CheckData, APIView):
        def get_request_type(self):
            return self.request.data

        def get_data(self):
            return self.request.data.get('check')

        def get(self, request, format=None):
            msg = self.check_data()
            return Response(msg, status=self.http_status)

        def post(self, request, format=None):
            return Response(self.check_data(), status=self.http_status)