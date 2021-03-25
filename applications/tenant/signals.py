from django.apps import apps
from django.db.models.signals import post_save, pre_save, post_delete
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model

TenantGroup = apps.get_model(*TenantConfig.ForeignKey.group.split('.'))
TenantRole = get_tenant_model(TenantConfig.ForeignKey.role)

def Roles(sender, instance, **kwargs):
    for role in TenantConfig.Default.group:
        role['group'] = instance
        role, status = TenantRole.objects.get_or_create(**role)
post_save.connect(Roles, TenantGroup    )

if TenantConfig.invitation_enable:
    from django.conf import settings
    from django.contrib.auth import get_user_model

    from django.template.loader import render_to_string
    
    from mighty.apps import MightyConfig
    from mighty.applications.logger import signals
    from mighty.applications.tenant import get_tenant_model
    from mighty.applications.user import choices
    from mighty.applications.tenant.apps import TenantConfig
    Invitation = get_tenant_model(TenantConfig.ForeignKey.invitation)

    def OnStatusChange(sender, instance, **kwargs):
        post_save.disconnect(OnStatusChange, sender=Invitation)
        if instance.status == choices.STATUS_ACCEPTED:
            kwargs = {
                'user': get_user_model().objects.get(user_email__email=instance.email),
                'invitation': instance,
                'group': instance.group
            }
            TenantModel = get_tenant_model()
            instance.tenant, status = TenantModel.objects.get_or_create(**kwargs)
            instance.status = choices.STATUS_READY
            instance.save()
        post_save.connect(OnStatusChange, Invitation)
    post_save.connect(OnStatusChange, Invitation)

    def SendMissiveInvitation(sender, instance, **kwargs):
        instance.status = choices.STATUS_ACCEPTED if instance.tenant else instance.status
        save_need = False
        if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
            from mighty.models import Missive
            if instance.status == choices.STATUS_TOSEND:
                if not instance.missive:
                    save_need = True
                    instance.missive = Missive(
                        content_type=instance.missives.content_type,
                        object_id=instance.id,
                        target=instance.email,
                        subject='Invitation a rejoindre la plateforme Octolo',
                    )
                    instance.status = choices.STATUS_PENDING
                else:
                    instance.missive.prepare()
                ctx = {
                    "company": str(instance.group),
                    "by": instance.by.representation,
                    "link": TenantConfig.invitation_url % { "domain": MightyConfig.domain, "uid": instance.uid, "token": instance.token }
                }
                instance.missive.html = render_to_string('tenant/invitation.html', ctx)
                instance.missive.txt = render_to_string('tenant/invitation.txt', ctx)
                instance.missive.save()
        if save_need:
            post_save.disconnect(SendMissiveInvitation, sender=Invitation)
            instance.save()
            post_save.connect(SendMissiveInvitation, Invitation)
    post_save.connect(SendMissiveInvitation, Invitation)