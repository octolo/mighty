from django.db.models import Q
from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from mighty.views import ModelViewSet
from mighty.applications.tenant.views.tenant.base import TenantBase
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model

RoleModel = get_tenant_model(TenantConfig.ForeignKey.role)

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

class TenantModelViewSet(ModelViewSet):
    group_pk = "uid"
    tenant_user = "tenant__user"
    group_way = "group"
    user_way = "tenant__user"
    role_model = RoleModel

    # Filter query
    def Q_is_tenant(self, prefix=""):
        return Q(**{prefix+self.group_way+"__in": self.tenant_groups})

    # Test
    def is_tenant(self, group, pk=None):
        if pk: return self.request.user.user_tenant.filter(**{"group__"+pk: group}).exists()
        return self.request.user.user_tenant.filter(group=group).exists()

    def has_role(self, role, pk=None):
        if pk: return self.request.user.user_tenant.filter(**{"roles__"+pk: role}).exists()
        return self.request.user.user_tenant.filter(roles=role).exists()

    def has_one_role(self, roles, pk=None):
        if pk: return self.request.user.user_tenant.filter(**{"roles__"+pk+"__in": roles}).exists()
        return self.request.user.user_tenant.filter(roles__in=roles).exists()

    # Properties
    @property
    def tenant_roles(self):
        return self.role_model.objects.filter(roles_tenant__user=self.request.user)

    @property
    def current_tenant_group(self):
        return self.request.user.current_tenant.group
    
    @property
    def tenant_groups(self):
        return [tenant.group for tenant in self.request.user.user_tenant.all()]

    @property
    def tenant_groups_pk(self):
        return [group.uid for group in self.tenant_groups]