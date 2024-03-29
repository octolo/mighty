from .custom import merge_accounts_signal

# TO CLEAN

from django.db.models.signals import post_save, pre_save, post_delete
from django.conf import settings
from django.contrib.auth import get_user_model

from mighty.applications.logger import signals
from mighty.applications.user.apps import UserConfig
from mighty.applications.user import get_user_email_model
from mighty.models import UserPhone


UserModel = get_user_model()
UserEmailModel = get_user_email_model()

if 'mighty.applications.logger' in settings.INSTALLED_APPS:
    pre_save.connect(signals.pre_change_log, UserModel)
    post_save.connect(signals.post_change_log, UserModel)

#def AfterAddAnEmail(sender, instance, **kwargs):
#    post_save.disconnect(AfterAddAnEmail, UserEmail)
#    if instance.default or instance.user.email is None:
#        UserEmail.objects.filter(user=instance.user).first()
#        instance.user.email = instance.email
#        instance.user.save()
#    post_save.connect(AfterAddAnEmail, UserEmail)
#post_save.connect(AfterAddAnEmail, UserEmail)

def AfterDeleteAnEmail(sender, instance, **kwargs):
    if not UserEmailModel.objects.filter(user=instance.user, **{UserConfig.ForeignKey.email_primary: True}).count():
        email = UserEmailModel.objects.filter(user=instance.user).first()
        if email:
            if apps.is_installed('allauth'):
                email.set_as_primary()
            else:
                setattr(instance.user, UserConfig.ForeignKey.email_primary, True)
                email.save()
post_delete.connect(AfterDeleteAnEmail, UserEmailModel)

#def AfterAddAPhone(sender, instance, **kwargs):
#    post_save.disconnect(AfterAddAPhone, UserPhone)
#    if instance.default or instance.user.phone is None:
#        UserPhone.objects.filter(user=instance.user).exclude(id=instance.id).update(default=False)
#        instance.user.phone = instance.phone
#        instance.user.save()
#    post_save.connect(AfterAddAPhone, UserPhone)
#post_save.connect(AfterAddAPhone, UserPhone)

def AfterDeleteAPhone(sender, instance, **kwargs):
    if not UserPhone.objects.filter(user=instance.user, default=True).count():
        phone = UserPhone.objects.filter(user=instance.user).first()
        if phone:
            phone.default = True
            phone.save()
post_delete.connect(AfterDeleteAPhone, UserPhone)

if UserConfig.invitation_enable:
    from django.template.loader import render_to_string
    from mighty.apps import MightyConfig
    from mighty.models import Invitation
    from mighty.applications.user import choices

    def OnStatusChange(sender, instance, **kwargs):
        if instance.status == choices.STATUS_ACCEPTED:
            if instance.user and instance.email not in instance.user.get_emails():
                getattr(instance.user, UserConfig.ForeignKey.email_related_name_attr).create(email=instance.email)
            elif not instance.user:
                post_save.disconnect(OnStatusChange, sender=Invitation)
                instance.user, status = UserModel.objects.get_or_create(
                    last_name=instance.last_name,
                    first_name=instance.first_name,
                    email=instance.email,
                    phone=instance.phone,
                )
                instance.user.save()
                instance.save()
                post_save.connect(OnStatusChange, Invitation)
    post_save.connect(OnStatusChange, Invitation)

    def SendMissiveInvitation(sender, instance, **kwargs):
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
                    "link": UserConfig.invitation_url % {"domain": MightyConfig.domain,  "uid": instance.uid, "token": instance.token}
                }
                instance.status = choices.STATUS_PENDING
                instance.missive.html = render_to_string('user/invitation.html', ctx)
                instance.missive.txt = render_to_string('user/invitation.txt', ctx)
                instance.missive.save()
        if save_need:
            post_save.disconnect(SendMissiveInvitation, sender=Invitation)
            instance.save()
            post_save.connect(SendMissiveInvitation, Invitation)
    post_save.connect(SendMissiveInvitation, Invitation)

# Signal that set the EmailAddres to verified=True
from django.apps import apps
if apps.is_installed('allauth'):
    from allauth.account.models import EmailAddress
    def EmailAddressSetVerified(sender, instance, **kwargs):
        if instance.verified:
            return
        instance.verified = True
        instance.save()
    post_save.connect(EmailAddressSetVerified, sender=EmailAddress)
