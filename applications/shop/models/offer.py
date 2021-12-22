from django.db import models
from django.template.defaultfilters import slugify

from mighty.apps import MightyConfig as conf
from mighty.models.base import Base
from mighty.models.image import Image
from mighty.applications.shop import choices

class Offer(Base, Image):
    # Related
    service = models.ManyToManyField('mighty.Service', blank=True, related_name='service_offer')

    name = models.CharField(max_length=255)
    named_id = models.CharField(max_length=255, db_index=True, null=True, editable=False)
    
    frequency = models.CharField(max_length=255, choices=choices.FREQUENCIES, default=choices.MONTH)
    duration = models.DurationField(blank=True, null=True, editable=False)
    
    # Price
    price = models.DecimalField(max_digits=9, decimal_places=2)
    is_custom = models.BooleanField(default=False)

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