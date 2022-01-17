from django.http import JsonResponse
from mighty.views import TemplateView
from mighty.models import ServiceData
from mighty.applications.dataprotect import choices as _c

class ServiceDataView(TemplateView):
    def prepare_categories(self):
        return { 
            category[0]: { 
                "name": category[0],
                "desc": getattr(_c, "%s_DESC" % category[0]),
                "svcs": [],
            } for category in _c.CATEGORY
        }

    def get_services(self):
        services = ServiceData.objects.all()
        categories = self.prepare_categories()
        for service in services:
            categories[service.category]["svcs"].append(service.as_json())
        return {k:v for k,v in categories.items() if v["svcs"]}
        
    def get_context_data(self, **kwargs):
        return self.get_services()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)
