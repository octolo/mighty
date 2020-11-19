from django.db.models.signals import post_save, pre_save, post_delete
from django.conf import settings
from mighty.apps import MightyConfig
from mighty.applications.logger import signals
from mighty.applications.tenant.apps import TenantConfig

if TenantConfig.invitation_enable:
    from mighty.applications.tenant import get_tenant_model
    from mighty.applications.user import choices
    from django.template.loader import render_to_string
    Invitation = get_tenant_model(settings.TENANT_INVITATION)

    def OnStatusChange(sender, instance, **kwargs):
        post_save.disconnect(OnStatusChange, sender=Invitation)

        from django.contrib.auth import get_user_model
        if instance.status == choices.STATUS_ACCEPTED:
            kwargs = {
                'user': get_user_model().objects.get(user_email__email=instance.email),
                'invitation': instance,
            }

            if instance.tenant:
                TenantModel = get_tenant_model(TenantConfig.ForeignKey.alternate)
                kwargs.update({'tenant': instance.tenant})
            else:
                TenantModel = get_tenant_model()
                kwargs.update({'group': instance.group})
            instance.content_object, status = TenantModel.objects.get_or_create(**kwargs)
            instance.save()


        post_save.connect(OnStatusChange, Invitation)
    post_save.connect(OnStatusChange, Invitation)

    def SendMissiveInvitation(sender, instance, **kwargs):
        instance.status = choices.STATUS_ACCEPTED if instance.object_id else instance.status
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
                        subject='subject: Tenant',
                    )
                    instance.status = choices.STATUS_PENDING
                else:
                    instance.missive.prepare()
                ctx = {
                    "company": str(instance.group),
                    "by": instance.by.representation,
                    "tenants_link": TenantConfig.invitation_url % { "domain": MightyConfig.domain }
                }
                instance.missive.html = render_to_string('tenant/invitation.html', ctx)
                instance.missive.txt = render_to_string('tenant/invitation.txt', ctx)
                instance.missive.save()
        if save_need:
            post_save.disconnect(SendMissiveInvitation, sender=Invitation)
            instance.save()
            post_save.connect(SendMissiveInvitation, Invitation)
    post_save.connect(SendMissiveInvitation, Invitation)