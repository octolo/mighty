from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

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
from mighty.functions import masking_email, masking_phone, get_model, url_domain
from mighty.models.base import Base
from mighty.fields import RichTextField, JSONField
from html2text import html2text

class MessengerModel(Base):
    in_test = False
    mode = models.CharField(max_length=8, choices=choices.MODE, default=choices.MODE_EMAIL)
    status = models.CharField(choices=choices.STATUS, default=choices.STATUS_PREPARE, max_length=9)
    priority = models.PositiveIntegerField(default=0, choices=choices.PRIORITIES)
    #address_window = models.BooleanField(default=False)

    name = models.CharField(max_length=255, blank=True, null=True)
    sender = models.CharField(max_length=255, blank=True, null=True)
    reply = models.CharField(max_length=255, blank=True, null=True)
    reply_name = models.CharField(max_length=255, blank=True, null=True)
    target = models.CharField(max_length=255, blank=True, null=True)
    service = models.CharField(max_length=255, blank=True, null=True)
    denomination = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)

    header_html = RichTextField(blank=True, null=True)
    footer_html = RichTextField(blank=True, null=True)

    subject = models.CharField(max_length=255)
    template = models.CharField(max_length=255, blank=True, null=True)

    html = RichTextField(blank=True, null=True)
    txt = models.TextField(blank=True, null=True)
    preheader = models.TextField(blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    context = JSONField(default=dict)

    default = ''
    attachments = []

    class Meta(Base.Meta):
        abstract = True
        ordering = ['-date_create',]

    @property
    def fullname(self):
        if self.last_name and self.first_name:
            return self.first_name+" "+self.last_name
        elif self.last_name or self.first_name:
            return self.first_name if self.first_name else self.last_name
        return None

    def need_to_send(self):
        raise NotImplementedError("Subclasses should implement need_to_send()")

    #def textify(self, html):
    #    from django.utils.html import strip_tags
    #    import re
    #    if self.template:
    #        html = re.findall('<body.*</body>', html, re.DOTALL)
    #        html = html[0]
    #    text_only = re.sub('[ \t]+', ' ', html)
    #    text_only = text_only.replace('\n ', '\n').strip()
    #    text_only = '\n'.join((txt for txt in text_only.splitlines() if txt.strip() != ""))
    #    return text_only
#
    #def set_txt(self):
    #    if self.html_format:
    #        self.txt = self.textify(self.html_format)

    def prepare(self):
        self.status = choices.STATUS_PREPARE

    def to_error(self):
        self.status = choices.STATUS_ERROR

    def prepare_mode(self):
        getattr(self, 'prepare_%s' % self.mode.lower())()

    def pre_save(self):
        #self.set_txt()
        self.set_backend()
        self.prepare_mode()
        self.need_to_send()

    def __str__(self):
        return '%s (%s)' % (self.masking, self.subject)

    def prepare_sms(self):
        self.html = 'not used for sms'

    def prepare_postal(self):
        self.txt = 'not used for postal'

    def prepare_postalar(self):
        self.txt = 'not used for postal'

    def prepare_name(self):
        if not self.name:
            self.name = conf.sender_name

    def prepare_email(self):
        self.prepare_name()
        if not self.sender:
            self.sender = conf.sender_email

    def prepare_emailar(self):
        if not self.sender:
            self.sender = conf.sender_email

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
    def content(self):
        return self.html if self.html else self.txt

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

    @property
    def html_format(self):
        return render_to_string(self.template, {"object": self, "domain_url": url_domain("", http=True) }) if self.template else self.html
