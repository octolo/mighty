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
