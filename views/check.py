from django.http import JsonResponse
from mighty.views.template import TemplateView
from mighty import translates as _
from mighty.functions import setting

# Check data side server
class CheckData(TemplateView):
    test_field = None

    def get_data(self):
        return self.request.GET.get('check')

    def get_queryset(self, queryset=None):
        self.model.objects.get(**{self.test_field: self.get_data()})

    def check_data(self):
        try:
            self.get_queryset()
        except self.model.DoesNotExist:        
            return { "message": _.no_errors }
        return { "code": "001", "error": _.error_already_exist }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.check_data(), safe=False, **response_kwargs)

if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.generics import RetrieveAPIView
    from rest_framework.response import Response
    
    class CheckData(CheckData, RetrieveAPIView):
        def get(self, request, format=None):
            return Response(self.check_data())