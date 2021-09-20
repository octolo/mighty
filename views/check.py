from django.http import JsonResponse
from mighty.views.template import TemplateView
from mighty import translates as _
from mighty.functions import setting

# Check data side server
class CheckData(TemplateView):
    test_field = None
    model = None

    def get_data(self):
        return self.request.GET.get('check')

    def get_queryset(self, queryset=None):
        self.model.objects.get(**{self.test_field: self.get_data()})

    def msg_no_errors(self):
        return { "message": _.no_errors, "valid": True }

    def msg_errors(self, errors):
        msg = { "valid": False }
        msg.update(errors)
        return msg

    def check_data(self):
        try:
            self.get_queryset()
        except self.model.DoesNotExist:        
            return self.msg_no_errors()
        return self.msg_errors({ "code": "001", "error": _.error_already_exist })

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.check_data(), safe=False, **response_kwargs)

if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.views import APIView
    from rest_framework.response import Response
    
    class CheckData(CheckData, APIView):
        def get_data(self):
            return self.request.data.get('check')

        def get(self, request, format=None):
            return Response(self.check_data())