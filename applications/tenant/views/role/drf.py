from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from mighty.applications.tenant.serializers import RoleSerializer
from mighty.applications.tenant.views.role.base import RoleBase


class RoleBase(RoleBase):
    serializer_class = RoleSerializer


class RoleList(RoleBase, ListAPIView):
    mandatories = ('group',)

    def get(self, request, format=None):
        return Response([self.get_fields(role) for role in self.get_queryset()])


class RoleDetail(RoleBase, RetrieveAPIView):
    def get(self, request, uid, action=None, format=None):
        tenant = self.get_object(uid)
        return Response(self.get_fields(tenant))
