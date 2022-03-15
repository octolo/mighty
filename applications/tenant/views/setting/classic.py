from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.validators import ValidationError

from mighty.functions import get_descendant_value
from mighty.views import DetailView, ListView, CheckData
from mighty.applications.tenant.views.setting.base import TenantSettingBase

@method_decorator(login_required, name='dispatch')
class TenantSettingList(TenantSettingBase, ListView):
    mandatories = ('group',)
    
    def get_context_data(self, **kwargs):
        return [self.get_fields(setting) for setting in self.get_queryset()]

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class TenantSettingDetail(TenantSettingBase, DetailView):
    def get_context_data(self, **kwargs):
        return self.get_fields(self.get_object(self.kwargs.get('uid', None)))

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class TenantSettingCheckData(CheckData):
    test_field = "name__iexact"

    def get_queryset(self, queryset=None):
        try:
            group = self.group_model.objects.get(uid=self.request.GET.get('group'))
            self.model.objects.get(**{self.test_field: self.request.GET.get('exist'), "group": group})
        except self.group_model.DoesNotExist:
            assert ValidationError('group mandatory')
