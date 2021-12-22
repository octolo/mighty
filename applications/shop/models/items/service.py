from django.db import models
from mighty.models.base import Base
from mighty.models.image import Image
import re

class Service(Base, Image):
    name = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=255, unique=True, blank=True, null=True)
    price = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=2)
    has_counter = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return "%s(%s)" % (self.name, self.code)

    def generate_key(self):
        return re.sub("[^a-zA-Z0-9]+", "", self.name).lower()

    def set_key(self):
        if not self.key:
            self.key = self.generate_key()

    def pre_save(self):
        self.set_key()