from rest_framework.generics import ListAPIView, RetrieveAPIView
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

from rest_framework import status
from rest_framework.generics import GenericAPIView
from sesame.utils import get_token

class Sesame(GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            token = get_token(request.user)

            return Response({"token": token}, status=status.HTTP_200_OK)
        except AttributeError:
            return Response({"error": "Tenant or user not found"}, status=status.HTTP_404_NOT_FOUND)
