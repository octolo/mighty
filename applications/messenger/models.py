from django.db import models
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from mighty.models.file import File
from mighty.models.base import Base
from mighty.applications.messenger import choices, translates as _, send_missive
from mighty.applications.messenger.apps import MessengerConfig as conf
from mighty.applications.user.apps import UserConfig as conf_user
from mighty.functions import masking_email, masking_phone
from mighty.applications.address.models import Address

from phonenumber_field.modelfields import PhoneNumberField
from django_ckeditor_5.fields import CKEditor5Field
from html2text import html2text

class Missive(Address):
    mode = models.CharField(max_length=6, choices=choices.MODE, default=choices.MODE_EMAIL)
    status = models.CharField(choices=choices.STATUS, default=choices.STATUS_PREPARE, max_length=8)
    priority = models.PositiveIntegerField(default=0, choices=choices.PRIORITIES)

    target = models.CharField(max_length=255)
    service = models.CharField(max_length=255, blank=True, null=True)
    denomination = models.CharField(max_length=255, blank=True, null=True)

    backend = models.CharField(max_length=255, editable=False)
    subject = models.CharField(max_length=255)
    msg_id = models.CharField(max_length=255, blank=True, null=True)

    header_html = CKEditor5Field(blank=True, null=True)
    footer_html = CKEditor5Field(blank=True, null=True)
    html = CKEditor5Field()
    txt = models.TextField()

    response = models.TextField(blank=True, null=True, editable=False)
    partner_id = models.CharField(max_length=255, blank=True, null=True, editable=False)
    code_error = models.CharField(max_length=255, blank=True, null=True, editable=False)
    trace = models.TextField(blank=True, null=True, editable=False)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    default = ''
    attachments = []

    class Meta(Base.Meta):
        abstract = True
        verbose_name = "missive"
        verbose_name_plural = "missives"
        permissions = [('can_check', _.permission_check),]
        ordering = ['-date_create',]

    def prepare_sms(self):
        self.html = 'not used for sms'

    def prepare_postal(self):
        self.txt = 'not used for postal'

    def prepare_email(self):
        pass

    def save(self, *args, **kwargs):
        if self.html and not self.txt: self.txt = html2text(self.html)
        if self.target is not None: self.email = self.target.lower()
        if self.status == choices.STATUS_PREPARE: send_missive(self)
        getattr(self, 'prepare_%s' % self.mode.lower())
        super().save(*args, **kwargs)

    def prepare(self):
        self.status = choices.STATUS_PREPARE

    def to_error(self):
        self.status = choices.STATUS_ERROR

    def to_sent(self):
        self.clear_errors()
        self.status = choices.STATUS_SENT

    def clear_errors(self):
        self.trace = None
        self.code_error = None

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
