from django.db.models import Q
from django.shortcuts import get_object_or_404

from mighty import filters
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model, filters as tenant_filters, fields as tenant_fields
from mighty.applications.tenant.serializers import RoleSerializer

RoleModel = get_tenant_model(TenantConfig.ForeignKey.role)
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)

class RoleBase:
    serializer_class = RoleSerializer
    model = RoleModel
    group_model = TenantGroup
    queryset = RoleModel.objectsB.all()
    group_way = "group"
    filters = [
        filters.SearchFilter(),
        tenant_filters.SearchByGroupUid(),
        tenant_filters.SearchByRoleUid(field='uid')
    ]

    @property
    def tenant_groups(self):
        return [tenant.group for tenant in self.request.user.user_tenant.all()]

    def Q_in_group(self, prefix=""):
        return Q(**{prefix+self.group_way+"__in": self.tenant_groups})

    def get_object(self):
        return get_object_or_404(self.model, **{"uid": self.kwargs.get('uid', None),})

    def get_fields(self, role):
        return {field: str(getattr(role, field)) for field in ('uid',) + tenant_fields.role}