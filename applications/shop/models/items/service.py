import re

from django.db import models

from mighty.applications.shop.models.realprice import RealPrice
from mighty.models.image import Image


class ShopService(RealPrice, Image):
    name = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    charge_at = models.PositiveIntegerField(default=1)
    has_counter = models.BooleanField(default=False)

    class Meta(RealPrice.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return '%s (%s €)' % (self.name, self.real_price)

    def generate_key(self):
        return re.sub(r'[^a-zA-Z0-9]+', '', self.name).lower()

    def set_key(self):
        if not self.key:
            self.key = self.generate_key()

    def pre_save(self):
        super().pre_save()
        self.set_key()
