from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.access import TenantAccess
from mighty.applications.tenant.apps import TenantConfig
from mighty.functions import setting
from mighty.permissions import MightyPermission, base_action, base_permission

TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)


class TenantRolePermission(MightyPermission, TenantAccess):
    group_way = 'group'
    role_way = 'roles'
    action_list = base_action
    check_list = base_permission
    check_retrieve = base_permission
    check_create = base_permission
    check_update = base_permission
    check_partial_update = base_permission
    check_destroy = base_permission
    check_others = base_permission

    @property
    def tenants(self):
        return self.user.user_tenant.all()

    @property
    def group(self):
        return TenantGroup

    # Tenant test
    def is_tenant(self, group, pk=None):
        if pk: return self.user.user_tenant.filter(**{self.group_way + '__' + pk: group}).exists()
        return self.user.user_tenant.filter(**{self.group_way: group}).exists()

    def has_role(self, role, pk=None):
        if pk: return self.user.user_tenant.filter(**{self.role_way + '__' + pk: role}).exists()
        return self.user.user_tenant.filter(**{self.role_way: role}).exists()

    def has_one_role(self, roles, pk=None):
        if pk: return self.user.user_tenant.filter(**{self.role_way + '__' + pk + '__in': roles}).exists()
        return self.user.user_tenant.filter(**{self.role_way + '__in': roles}).exists()


if 'rest_framework' in setting('INSTALLED_APPS'):
    from mighty.permissions import MightyPermissionDrf

    class TenantRolePermissionDrf(MightyPermissionDrf, TenantRolePermission): pass
