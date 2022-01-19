from django.http import JsonResponse
from mighty.views import TemplateView
from mighty.models import ServiceData
from mighty.applications.dataprotect import choices as _c

class ServiceDataView(TemplateView):
    services = None
    
    def prepare_categories(self):
        return [{ 
                "name": category[1],
                "category": category[0],
                "desc": getattr(_c, "%s_DESC" % category[0]),
                "svcs": self.get_svcs_category(category[0])
        } for category in _c.CATEGORY]

    def get_svcs_category(self, category):
        return [service.as_json() for service in self.services if service.category == category]

    def get_services(self):
        self.services = ServiceData.objects.all()
        return [category for category in self.prepare_categories() if category["svcs"]]
        
    def get_context_data(self, **kwargs):
        return self.get_services()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)
