from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from mighty.applications.messenger import (
    choices, translates as _,
    missive_backend_email,
    missive_backend_emailar,
    missive_backend_postal,
    missive_backend_postalar,
    missive_backend_sms,
    missive_backend_web,
    missive_backend_app,
)
from mighty.applications.messenger.apps import MessengerConfig as conf
from mighty.functions import masking_email, masking_phone, get_model
from mighty.models.base import Base

from django_ckeditor_5.fields import CKEditor5Field
from html2text import html2text

class MessengerModel(Base):
    mode = models.CharField(max_length=8, choices=choices.MODE, default=choices.MODE_WEB)
    status = models.CharField(choices=choices.STATUS, default=choices.STATUS_PREPARE, max_length=8)
    priority = models.PositiveIntegerField(default=0, choices=choices.PRIORITIES)
    
    target = models.CharField(max_length=255)
    service = models.CharField(max_length=255, blank=True, null=True)
    denomination = models.CharField(max_length=255, blank=True, null=True)

    header_html = CKEditor5Field(blank=True, null=True)
    footer_html = CKEditor5Field(blank=True, null=True)

    subject = models.CharField(max_length=255)
    html = CKEditor5Field()
    txt = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    default = ''
    attachments = []

    class Meta(Base.Meta):
        abstract = True
        ordering = ['-date_create',]

    def need_to_send(self):
        raise NotImplementedError("Subclasses should implement need_to_send()")

    def set_txt(self):
        if self.html and not self.txt:
            self.txt = html2text(self.html)

    def prepare(self):
        self.status = choices.STATUS_PREPARE

    def to_error(self):
        self.status = choices.STATUS_ERROR

    def prepare_mode(self):
        getattr(self, 'prepare_%s' % self.mode.lower())()

    def pre_save(self):
        self.set_txt()
        self.set_backend()
        self.prepare_mode()
        self.need_to_send()
        getattr(self, 'prepare_%s' % self.mode.lower())

    def __str__(self):
        return '%s (%s)' % (self.masking, self.subject)

    def prepare_sms(self):
        self.html = 'not used for sms'

    def prepare_postal(self):
        self.txt = 'not used for postal'

    def prepare_email(self):
        pass

    def prepare_web(self):
        pass

    def set_backend(self):
        self.backend = conf.missive_backends
        if self.mode == choices.MODE_EMAIL:
            self.backend = missive_backend_email()
        if self.mode == choices.MODE_EMAILAR:
            self.backend = missive_backend_emailar()
        if self.mode == choices.MODE_POSTAL:
            self.backend = missive_backend_postal()
        if self.mode == choices.MODE_POSTALAR:
            self.backend = missive_backend_postalar()
        if self.mode == choices.MODE_SMS:
            self.backend = missive_backend_sms()
        if self.mode == choices.MODE_WEB:
            self.backend = missive_backend_web()
        if self.mode == choices.MODE_APP:
            self.backend = missive_backend_app()

    @property
    def masking_email(self):
        return masking_email(self.target)
    
    @property
    def masking_phone(self):
        return masking_phone(self.target)

    @property
    def masking(self):
        if self.mode == choices.MODE_SMS:
            return self.masking_phone
        elif self.mode == choices.MODE_EMAIL:
            return self.masking_email
        elif self.mode == choices.MODE_POSTAL:
            return self.raw_address
        return self.target

    @property
    def model_missive(self):
        return get_model('mighty', 'Missive')

    @property
    def model_notification(self):
        return get_model('mighty', 'Notification')

