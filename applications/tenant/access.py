from django.db.models import Q
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model

TenantModel = get_tenant_model(TenantConfig.ForeignKey.tenant)
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)
RoleModel = get_tenant_model(TenantConfig.ForeignKey.role)

class TenantAccess:
    group_pk = "uid"
    tenant_user = "tenant__user"
    group_way = "group"
    user_way = "tenant__user"
    role_model = RoleModel
    tenant_model = TenantModel
    group_model = TenantGroup

    def get_group_model(self, uid, field="uid"):
        return self.group_model.objects.get(**{field: uid})

    # Query filter
    def Q_current_group(self, prefix=""):
        return Q(**{prefix+self.group_way: self.current_group})

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
    def current_group(self):
        named_id = self.kwargs.get('group_named_id')
        group_uid = self.request.data.get('group')
        if named_id: 
            return self.group_model.objects.get(named_id=named_id)
        elif group_uid:
            return self.group_model.objects.get(uid=group_uid)
        return self.current_tenant_group

    @property
    def current_group_uid(self):
        return self.current_group.uid

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
        return [group.pk for group in self.tenant_groups]
