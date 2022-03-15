from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from mighty.views import ModelViewSet
from mighty.applications.tenant.views.tenant.base import TenantBase
from mighty.applications.tenant.access import TenantAccess
from mighty.applications.tenant.serializers import TenantSerializer

class TenantBase(TenantBase):
    serializer_class = TenantSerializer

class TenantList(TenantBase, ListAPIView):
    def get(self, request, format=None):
        return Response(self.get_tenants())

class TenantDetail(TenantBase, RetrieveAPIView):
    def get(self, request, uid, action=None, format=None):
        tenant = self.get_object()
        return Response(self.get_fields(tenant))

class CurrentTenant(TenantBase, RetrieveAPIView):
    def get(self, request, uid, action=None, format=None):
        tenant = self.get_object()
        self.request.user.current_tenant = tenant
        self.request.user.save()
        return Response(self.get_fields(tenant))

class TenantModelViewSet(ModelViewSet, TenantAccess):
    pass