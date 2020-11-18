from django.db.models.signals import post_save, pre_save, post_delete
from django.conf import settings

from mighty.applications.logger import signals
from mighty.applications.user.apps import UserConfig
from mighty.models import Email, Phone, User

if 'mighty.applications.logger' in settings.INSTALLED_APPS:
    pre_save.connect(signals.pre_change_log, User)
    post_save.connect(signals.post_change_log, User)

def AfterAddAnEmail(sender, instance, **kwargs):
    post_save.disconnect(AfterAddAnEmail, Email)
    if instance.default or instance.user.email is None:
        Email.objects.filter(user=instance.user).first()
        instance.user.email = instance.email
        instance.user.save()
    post_save.connect(AfterAddAnEmail, Email)
post_save.connect(AfterAddAnEmail, Email)

def AfterDeleteAnEmail(sender, instance, **kwargs):
    if not Email.objects.filter(user=instance.user, default=True).count():
        email = Email.objects.filter(user=instance.user).first()
        if email:
            email.default = True
            email.save()
post_delete.connect(AfterDeleteAnEmail, Email)

def AfterAddAPhone(sender, instance, **kwargs):
    post_save.disconnect(AfterAddAPhone, Phone)
    if instance.default or instance.user.phone is None:
        Phone.objects.filter(user=instance.user).exclude(id=instance.id).update(default=False)
        instance.user.phone = instance.phone
        instance.user.save()
    post_save.connect(AfterAddAPhone, Phone)
post_save.connect(AfterAddAPhone, Phone)

def AfterDeleteAPhone(sender, instance, **kwargs):
    if not Phone.objects.filter(user=instance.user, default=True).count():
        phone = Phone.objects.filter(user=instance.user).first()
        if phone:
            phone.default = True
            phone.save()
post_delete.connect(AfterDeleteAPhone, Phone)

if UserConfig.invitation_enable:
    from django.template.loader import render_to_string
    from mighty.apps import MightyConfig
    from mighty.models import Invitation
    from mighty.applications.user import choices

    def OnChangeInvitation(sender, instance, **kwargs):
        instance.status = choices.STATUS_ACCEPTED if instance.user else instance.status
        save_need = False
        if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
            from mighty.models import Missive
            if instance.status in [choices.STATUS_TOSEND, choices.STATUS_PENDING]:
                if not instance.missive:
                    save_need = True
                    instance.missive = Missive(
                        content_type=instance.missives.content_type,
                        object_id=instance.id,
                        target=instance.email,
                        subject='subject: Invitation',
                    )
                elif instance.is_expired:
                    instance.new_token()
                    instance.missive.prepare()
                ctx = {
                    "website": MightyConfig.domain,
                    "by": instance.by.representation,
                    "invitation_link": UserConfig.invitation_url % {"domain": MightyConfig.domain,  "uid": instance.uid, "token": instance.token}
                }
                instance.status = choices.STATUS_PENDING
                instance.missive.html = render_to_string('user/invitation.html', ctx)
                instance.missive.txt = render_to_string('user/invitation.txt', ctx)
                instance.missive.save()
        if save_need:
            post_save.disconnect(OnChangeInvitation, sender=Invitation)
            instance.save()
            post_save.connect(OnChangeInvitation, Invitation)
    post_save.connect(OnChangeInvitation, Invitation)