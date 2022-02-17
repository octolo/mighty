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
    mode = models.CharField(max_length=20, choices=_c.MODE_SIGNATORY, default=_c.EMAIL)
    location = JSONField(blank=True, null=True)
    color = ColorField(format="hexa", default=generate_random_color)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        abstract = True

    def pre_save(self):
        if not self.email: self.email = self.signatory_email
        if not self.phone: self.phone = self.signatory_phone

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
    @property
    def follow_model(self):
        from mighty.functions import get_model
        label, model = conf.signatory_relation.split(".")
        return get_model(label, model)

    def getattr_signatory(self, attr):
        if hasattr(self.signatory, attr):
            return getattr(self.signatory, attr)
        raise NotImplementedError("Signatory need attribute : %s" % attr)
        

    # SIGNATORY NEEDS
    @property
    def fullname(self):
        return self.signatory_fullname
    @property
    def picture(self):
        return self.signatory_picture
    @property
    def signatory_fullname(self):
        return self.getattr_signatory("signatory_fullname")
    @property
    def signatory_picture(self):
        return self.getattr_signatory("signatory_picture")
    @property
    def signatory_phone(self):
        return self.getattr_signatory("signatory_phone")
    @property
    def signatory_email(self):
        return self.getattr_signatory("signatory_email")
    @property
    def has_phone(self): 
        return True if self.phone else False
    @property
    def has_email(self): 
        return True if self.email else False
