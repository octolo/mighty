from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from mighty.applications.tenant.views.tenant.base import TenantBase
from mighty.views import DetailView, ListView


@method_decorator(login_required, name='dispatch')
class TenantList(TenantBase, ListView):
    def get_context_data(self, **kwargs):
        return self.get_tenants()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)


@method_decorator(login_required, name='dispatch')
class TenantDetail(TenantBase, DetailView):
    def get_context_data(self, **kwargs):
        return self.get_fields(self.get_object())

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)


@method_decorator(login_required, name='dispatch')
class CurrentTenant(TenantBase, DetailView):
    def get_context_data(self, **kwargs):
        tenant = self.get_object()
        return self.get_fields(tenant)

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)
