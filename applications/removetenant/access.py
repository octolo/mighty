from django.db.models import Q
from mighty.request_access import RequestAccess
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model

class TenantAccess(RequestAccess):
    group_pk = "uid"
    tenant_user = "tenant__user"
    group_way = "group"
    user_way = "tenant__user"

    @property
    def group_model(self):
        return get_tenant_model(TenantConfig.ForeignKey.group)

    @property
    def tenant_model(self):
        return get_tenant_model(TenantConfig.ForeignKey.tenant)

    def get_group_model(self, uid, field="uid"):
        return self.group_model.objects.get(**{field: uid})

    # Query filter
    def Q_current_group(self, prefix=""):
        return Q(**{prefix+self.group_way: self.current_group})

    def Q_groups_associated(self, prefix=""):
        return Q(**{prefix+self.group_way+"__in": self.tenant_groups})

    # Filter query
    def Q_is_tenant(self, prefix=""):
        return Q(**{prefix+self.group_way+"__in": self.tenant_groups})

    # Test
    def is_tenant(self, group, pk=None):
        if pk: return self.request_access.user.user_tenant.filter(**{"group__"+pk: group}).exists()
        return self.request_access.user.user_tenant.filter(group=group).exists()

    # Properties
    @property
    def current_group(self):
        if self.request_access:
            named_id = self.request_access.parser_context['kwargs'].get('group_named_id')
            group_uid = self.request_access.data.get('group')
            if named_id:
                return self.group_model.objects.get(named_id=named_id)
            elif group_uid:
                return self.group_model.objects.get(uid=group_uid)
            return self.current_tenant_group
        return None

    @property
    def current_group_uid(self):
        return self.current_group.uid

    @property
    def current_tenant_group(self):
        return self.request_access.user.current_tenant.group

    @property
    def tenant_groups(self):
        return [tenant.group for tenant in self.request_access.user.user_tenant.all()]

    @property
    def tenant_groups_pk(self):
        return self.request_access.user.user_tenant.values_list("group_id", flat=True)
