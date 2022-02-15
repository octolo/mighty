from django.db import models
from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.applications.signature.apps import SignatureConfig as conf
from mighty.applications.signature import choices as _c
from colorfield.fields import ColorField
import random

def generate_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

class TransactionSignatory(Base):
    transaction = models.ForeignKey(conf.transaction_relation, on_delete=models.CASCADE, related_name="transaction_to_signatory")
    signatory = models.ForeignKey(conf.signatory_relation, on_delete=models.CASCADE)
    backend_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=_c.STATUS_SIGNATORY, default=_c.PREPARATION)
    role = models.CharField(max_length=20, choices=_c.ROLE_SIGNATORY, default=_c.OBSERVER)
    location = JSONField(blank=True, null=True)
    color = ColorField(format="hexa", default=generate_random_color)

    class Meta:
        abstract = True

    def add_signatory_id_to_cache(self):
        self.signatory.add_cache(self.transation.backend, {"id": self.signatory_id})

    def set_height(self, height):
        self.location["height"] = height
    def set_width(self, width):
        self.location["width"] = width
    def set_coordx(self, x):
        self.location["x"] = x
    def set_coordy(self, y):
        self.location["y"] = y

    def get_height(self):
        return self.location.get("height")
    def get_width(self):
        return self.location.get("width")
    def get_coordx(self):
        return self.location.get("x")
    def get_coordy(self):
        return self.location.get("y")

    @property
    def height(self):
        return self.get_height()
    @property
    def width(self):
        return self.get_width()
    @property
    def coordx(self):
        return self.get_coordx()
    @property
    def coordy(self):
        return self.get_coordy()
