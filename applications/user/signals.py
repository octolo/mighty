from django.db import models
from django.db.models.signals import post_save, post_delete
from mighty.models.applications.user import Email, Phone

def AfterAddAnEmail(sender, instance, created, **kwargs):
    post_save.disconnect(AfterAddAnEmail, Email)
    if instance.default:
        Email.objects.filter(user=instance.user).exclude(id=instance.id).update(default=False)
        instance.user.email = instance.email
        instance.user.save()
    post_save.connect(AfterAddAnEmail, Email)
post_save.connect(AfterAddAnEmail, Email)

def AfterAddAPhone(sender, instance, created, **kwargs):
    post_save.disconnect(AfterAddAPhone, Phone)
    if instance.default or instance.user.phone is None:
        Phone.objects.filter(user=instance.user).exclude(id=instance.id).update(default=False)
        instance.user.phone = instance.phone
        instance.user.save()
    post_save.connect(AfterAddAPhone, Phone)
post_save.connect(AfterAddAPhone, Phone)