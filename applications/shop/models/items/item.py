import re

from django.db import models

from mighty.applications.shop.models.realprice import RealPrice


class ShopItem(RealPrice):
    name = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    service = models.ForeignKey('mighty.ShopService', on_delete=models.SET_NULL, null=True, blank=True, related_name='service_item')

    class Meta(RealPrice.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return '%s (%s €)' % (self.name, self.price)

    def generate_key(self):
        return re.sub(r'[^a-zA-Z0-9]+', '', self.name).lower()

    def set_key(self):
        if not self.key:
            self.key = self.generate_key()

    def pre_save(self):
        self.set_key()
