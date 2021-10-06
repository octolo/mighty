from django.db import models
from django.template.defaultfilters import slugify

from mighty.apps import MightyConfig as conf
from mighty.models.base import Base
from mighty.models.image import Image
from mighty.applications.shop import generate_code_service, generate_code_offer, choices
import re

class Service(Base, Image):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, default=generate_code_service, unique=True)
    key = models.CharField(max_length=255, unique=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return "%s(%s)" % (self.name, self.code)

    def set_key(self):
        self.key = re.sub("[^a-zA-Z0-9]+", "", self.name).lower()

    def pre_save(self):
        self.set_key()

class Offer(Base, Image):
    named_id = models.CharField(max_length=255, db_index=True, null=True, editable=False)
    name = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255, choices=choices.FREQUENCIES, default=choices.MONTH)
    duration = models.DurationField(blank=True, null=True, editable=False)
    price = models.FloatField()
    service = models.ManyToManyField('mighty.Service', blank=True, related_name='service_offer')
    price_tenant = models.FloatField(default=0.0)
    is_custom = models.BooleanField(default=False)
    code = models.CharField(max_length=50, default=generate_code_offer, unique=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_frequency_display())

    def set_named_id(self):
        self.named_id = conf.named_tpl % {"named": slugify(self.name), "id": self.id}

    def pre_update(self):
        self.set_named_id()

    def post_create(self):
        if not self.named_id:
            self.save()