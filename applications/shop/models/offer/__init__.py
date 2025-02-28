from django.db import models
from django.template.defaultfilters import slugify

from mighty.applications.shop import choices
from mighty.applications.shop.models.realprice import RealPrice
from mighty.apps import MightyConfig as conf
from mighty.models.image import Image


class Offer(RealPrice, Image):
    name = models.CharField(max_length=255)
    named_id = models.CharField(max_length=255, db_index=True, null=True, editable=False)
    frequency = models.CharField(max_length=255, choices=choices.FREQUENCIES, default=choices.MONTH)
    duration = models.DurationField(blank=True, null=True, editable=False)
    is_custom = models.BooleanField(default=False)
    price_tenant = models.PositiveIntegerField(default=0)
    service = models.ManyToManyField('mighty.ShopService', blank=True, related_name='service_offer')
    service_tenant = models.ForeignKey('mighty.ShopService', on_delete=models.SET_NULL, blank=True, null=True)
    need_quotation = models.BooleanField(default=False)

    class Meta(RealPrice.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_frequency_display()})'

    @property
    def real_price_tenant(self):
        return self.price_tenant / 100

    def set_named_id(self):
        self.named_id = conf.named_tpl % {'named': slugify(self.name), 'id': self.id}

    def pre_update(self):
        self.set_named_id()

    def post_create(self):
        if not self.named_id:
            self.save()
