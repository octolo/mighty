from mighty.functions import setting

if 'rest_framework' in setting('INSTALLED_APPS'):
    from mighty.applications.tenant.apps import TenantConfig
    from mighty.applications.tenant import get_tenant_model
    from mighty.permissions import MightyPermission, base_action, base_permission
    from rest_framework.permissions import BasePermission

    Role = get_tenant_model(TenantConfig.ForeignKey.role)
    TenantModel = get_tenant_model(TenantConfig.ForeignKey.tenant)
    TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)
    
    class TenantRolePermission(MightyPermission):
        role_model = Role
        tenant_model = TenantModel
        group_model = TenantGroup

        group_pk = "uid"
        tenant_user = "tenant__user"

        action_list = base_action
        check_list = base_permission
        check_retrieve = base_permission
        check_create = base_permission
        check_update = base_permission
        check_partial_update = base_permission
        check_destroy = base_permission
        check_others = base_permission

        def get_group_model(self, uid):
            return self.group_model.objects.get(uid=uid)

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

        # Properties
        @property
        def tenant_roles(self):
            return self.role_model.objects.filter(roles_tenant__user=self.user)

        @property
        def current_tenant_group(self):
            return self.user.current_tenant.group
        
        @property
        def tenant_groups(self):
            return self.user.user_tenant.all()

        @property
        def tenant_groups_pk(self):
            return [group.uid for group in self.tenant_groups]
