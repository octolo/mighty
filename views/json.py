from django.views.generic.base import TemplateView
from mighty.views.base import BaseView
from django.http import JsonResponse

class JsonView(BaseView, TemplateView):
    is_safe = True

    def do_post(self, request, *args, **kwargs):
        return {}

    def post(self, request, *args, **kwargs):
        data = self.do_post(request, *args, **kwargs)
        return JsonResponse(data, safe=self.is_safe)

    def do_get(self, request, *args, **kwargs):
        return {}

    def get(self, request, *args, **kwargs):
        data = self.do_get(request, *args, **kwargs)
        return JsonResponse(data, safe=self.is_safe)
