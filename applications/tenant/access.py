from django.db.models import Q

from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.apps import TenantConfig
from mighty.functions import get_descendant_value
from mighty.request_access import RequestAccess


class TenantAccess(RequestAccess):
    group_pk = 'uid'
    tenant_user = 'tenant__user'
    group_way = 'group'
    user_way = 'tenant__user'

    @property
    def group_model(self):
        return get_tenant_model(TenantConfig.ForeignKey.group)

    @property
    def tenant_model(self):
        return get_tenant_model(TenantConfig.ForeignKey.tenant)

    @property
    def role_model(self):
        return get_tenant_model(TenantConfig.ForeignKey.role)

    def get_group_model(self, uid, field='uid'):
        return self.group_model.objects.get(**{field: uid})

    # Query filter
    def Q_current_group(self, prefix=''):
        return Q(**{prefix + self.group_way: self.current_group})

    def Q_groups_associated(self, prefix=''):
        return Q(**{prefix + self.group_way + '__in': self.tenant_groups})

    # Filter query
    def Q_is_tenant(self, prefix=''):
        return Q(**{prefix + self.group_way + '__in': self.tenant_groups})

    # Test
    def is_tenant(self, group, pk=None):
        if pk:
            return self.request_access.user.user_tenant.filter(**{
                'group__' + pk: group
            }).exists()
        return self.request_access.user.user_tenant.filter(group=group).exists()

    def has_role(self, role, pk=None):
        if pk:
            return self.request_access.user.user_tenant.filter(**{
                'roles__' + pk: role
            }).exists()
        return self.request_access.user.user_tenant.filter(roles=role).exists()

    def has_one_role(self, roles, pk=None):
        if pk:
            return self.request_access.user.user_tenant.filter(**{
                'roles__' + pk + '__in': roles
            }).exists()
        return self.request_access.user.user_tenant.filter(
            roles__in=roles
        ).exists()

    # Properties
    @property
    def current_group(self):
        if self.request_access:
            named_id = self.request_access.parser_context['kwargs'].get(
                'group_named_id'
            )
            if named_id:
                return self.group_model.objects.get(named_id=named_id)
            group_uid = self.request_access.data.get('group')
            if group_uid:
                return self.group_model.objects.get(uid=group_uid)
            return self.current_tenant_group
        return None

    @property
    def current_group_uid(self):
        return self.current_group.uid

    @property
    def tenant_roles(self):
        return self.role_model.objects.filter(
            roles_tenant__user=self.request_access.user
        )

    @property
    def tenant_roles_pk(self):
        return self.role_model.objects.filter(
            roles_tenant__user=self.request_access.user
        ).values_list('pk', flat=True)

    @property
    def current_tenant_group(self):
        return get_descendant_value(
            'current_tenant.group', self.request_access.user
        ) or self.current_group # risk of infinite loop

    @property
    def tenant_groups(self):
        return [
            tenant.group
            for tenant in self.request_access.user.user_tenant.all()
        ]

    @property
    def tenant_groups_pk(self):
        return self.request_access.user.user_tenant.values_list(
            'group_id', flat=True
        )
