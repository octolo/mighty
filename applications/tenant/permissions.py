from mighty.functions import setting
from mighty.permissions import MightyPermission, base_action, base_permission
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant.access import TenantAccess

class TenantRolePermission(MightyPermission, TenantAccess):
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

    # Tenant test
    def is_tenant(self, group, pk=None):
        if pk: return self.user.user_tenant.filter(**{"group__"+pk: group}).exists()
        return self.user.user_tenant.filter(group=group).exists()

    def has_role(self, role, pk=None):
        if pk: return self.user.user_tenant.filter(**{"roles__"+pk: role}).exists()
        return self.user.user_tenant.filter(roles=role).exists()

    def has_one_role(self, roles, pk=None):
        if pk: return self.user.user_tenant.filter(**{"roles__"+pk+"__in": roles}).exists()
        return self.user.user_tenant.filter(roles__in=roles).exists()

if 'rest_framework' in setting('INSTALLED_APPS'):
    from mighty.permissions import MightyPermissionDrf

    class TenantRolePermissionDrf(MightyPermissionDrf, TenantRolePermission): pass
    
