from django.db.models import Q

from mighty import filters
from mighty.applications.tenant import fields as tenant_fields
from mighty.applications.tenant import filters as tenant_filters
from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.apps import TenantConfig
from mighty.views import FoxidView

RoleModel = get_tenant_model(TenantConfig.ForeignKey.role)
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)


class RoleBase(FoxidView):
    model = RoleModel
    group_model = TenantGroup
    queryset = RoleModel.objectsB.all()
    group_way = 'group'
    filters = [
        filters.SearchFilter(),
        tenant_filters.SearchByGroupUid(),
        tenant_filters.SearchByRoleUid(id='uid', field='uid')
    ]

    @property
    def tenant_groups(self):
        return [tenant.group for tenant in self.request.user.user_tenant.all()]

    def Q_in_group(self, prefix=''):
        return Q(**{prefix + self.group_way + '__in': self.tenant_groups})

    def get_queryset(self):
        return super().get_queryset().filter(group__in=self.tenant_groups)

    def get_object(self, uid):
        return self.get_queryset().get(uid=uid)

    def get_fields(self, role):
        return {field: str(getattr(role, field)) for field in ('uid', *tenant_fields.role)}
