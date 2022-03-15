from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from mighty.applications.tenant.views.setting.base import TenantSettingBase
from mighty.applications.tenant.serializers import TenantSettingSerializer

class TenantSettingBase(TenantSettingBase):
    serializer_class = TenantSettingSerializer

class TenantSettingList(TenantSettingBase, ListAPIView):
    mandatories = ('group',)
    
    def get(self, request, format=None):
        return Response([self.get_fields(setting) for setting in self.get_queryset()])

class TenantSettingDetail(TenantSettingBase, RetrieveAPIView):
    def get(self, request, uid, action=None, format=None):
        tenant = self.get_object(uid)
        return Response(self.get_fields(tenant))
