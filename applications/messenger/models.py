from django.db import models
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from mighty.models.base import Base
from mighty.applications.messenger import choices, translates as _, send_missive
from mighty.applications.messenger.apps import MessengerConfig as conf
from mighty.applications.user.apps import UserConfig as conf_user
from mighty.functions import masking_email, masking_phone
from mighty.applications.address.models import Address

from phonenumber_field.modelfields import PhoneNumberField
from django_ckeditor_5.fields import CKEditor5Field

class Missive(Base):
    mode = models.CharField(max_length=6, choices=choices.MODE, default=choices.MODE_EMAIL)
    status = models.CharField(choices=choices.STATUS, default=choices.STATUS_PREPARE, max_length=8)
    target = models.CharField(max_length=255)
    backend = models.CharField(max_length=255, editable=False)
    response = models.TextField(editable=False)
    subject = models.CharField(max_length=255)
    html = CKEditor5Field()
    txt = models.TextField()
    default = ''

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta(Base.Meta):
        abstract = True
        verbose_name = "missive"
        verbose_name_plural = "missives"
        permissions = [('can_check', _.permission_check),]
        ordering = ['-date_create',]

    def save(self, *args, **kwargs):
        if self.target is not None: self.email = self.target.lower()
        if self.status == choices.STATUS_PREPARE:
            send_missive(self)
        super().save(*args, **kwargs)

    def prepare(self):
        self.status = choices.STATUS_PREPARE

    @property
    def masking_email(self):
        return masking_email(self.target)
    
    @property
    def masking_phone(self):
        return masking_phone(self.target)

    @property
    def masking(self):
        return self.masking_phone if self.mode == choices.MODE_SMS else self.masking_email

    def __str__(self):
        return '%s (%s)' % (self.masking, self.subject)

    def get_backend(self):
        backend = import_string(self.backend)()
        return backend

    def check_status(self):
        backend = self.get_backend()
        return getattr(backend, 'check_%s' % self.mode.lower())(self)

    def email(self):
        return self.user.email
    email.short_description = _.email
    email.admin_order_field = 'user__email'

    def phone(self):
        return self.user.phone
    phone.short_description = _.phone
    phone.admin_order_field = 'user__phone'

    def postal(self):
        return self.user.address
    postal.short_description = _.postal
    postal.admin_order_field = 'user__address'

from mighty.models.file import File
class Attachment(Base, File):
    missive = models.ForeignKey(conf.missive, on_delete=models.CASCADE, related_name="attachement_missive")
    
    class Meta(Base.Meta):
        abstract = True