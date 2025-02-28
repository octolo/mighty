from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed

from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.apps import TenantConfig

UserModel = get_user_model()
TenantModel = get_tenant_model()
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)
TenantRole = get_tenant_model(TenantConfig.ForeignKey.role)

# def Roles(sender, instance, **kwargs):
#    for role in TenantConfig.roles:
#        role['group'] = instance
#        role, status = TenantRole.objects.get_or_create(**role)
# post_save.connect(Roles, TenantGroup)


def setTenantAuto(sender, instance, **kwargs):
    user = UserModel.objects.get(id=instance.update_by.split('.')[0])
    if hasattr(instance, 'group'):
        if not instance.group:
            instance.group = user.current_tenant.group
            instance.save()
    elif not instance.user:
        instance.user = user
        instance.save()


def AddOrRemoveRoles(sender, instance, action, **kwargs):
    if action in {'post_add', 'post_remove'}:
        roles = TenantRole.objects.filter(id__in=kwargs.get('pk_set'))
        for role in roles:
            role.save()


m2m_changed.connect(AddOrRemoveRoles, sender=TenantModel.roles.through)
