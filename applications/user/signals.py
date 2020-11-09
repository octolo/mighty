from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth import get_user_model

from mighty.applications.logger import signals
from mighty.models import Email, Phone, User

def AfterAddAnEmail(sender, instance, **kwargs):
    post_save.disconnect(AfterAddAnEmail, Email)
    if instance.default or instance.user.email is None:
        Email.objects.filter(user=instance.user).first()
        instance.user.email = instance.email
        instance.user.save()
    post_save.connect(AfterAddAnEmail, Email)

def AfterDeleteAnEmail(sender, instance, **kwargs):
    if not Email.objects.filter(user=instance.user, default=True).count():
        email = Email.objects.filter(user=instance.user).first()
        if email:
            email.default = True
            email.save()

def AfterAddAPhone(sender, instance, **kwargs):
    post_save.disconnect(AfterAddAPhone, Phone)
    if instance.default or instance.user.phone is None:
        Phone.objects.filter(user=instance.user).exclude(id=instance.id).update(default=False)
        instance.user.phone = instance.phone
        instance.user.save()
    post_save.connect(AfterAddAPhone, Phone)

def AfterDeleteAPhone(sender, instance, **kwargs):
    if not Phone.objects.filter(user=instance.user, default=True).count():
        phone = Phone.objects.filter(user=instance.user).first()
        if phone:
            phone.default = True
            phone.save()

post_save.connect(AfterAddAnEmail, Email)
post_save.connect(AfterAddAPhone, Phone)

post_delete.connect(AfterDeleteAnEmail, Email)
post_delete.connect(AfterDeleteAPhone, Phone)

pre_save.connect(signals.pre_change_log, User)
post_save.connect(signals.post_change_log, User)