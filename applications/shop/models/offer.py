from django.db import models
from mighty.models.base import Base
from mighty.applications.shop import generate_code_type, choices

class Service(Base):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, default=generate_code_type, unique=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return "%s(%s)" % (self.name, self.code)

class Offer(Base):
    name = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255, choices=choices.FREQUENCIES, default='ONUSE')
    duration = models.DurationField(blank=True, null=True, editable=False)
    price = models.FloatField()
    service = models.ManyToManyField('mighty.Service', blank=True, related_name='service_offer')
    price_tenant = models.FloatField(default=0.0)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_frequency_display())