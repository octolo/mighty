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
    color = ColorField(format="hexa", default=generate_random_color)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "%s(%s)" % (str(self.signatory), str(self.transaction))

    class Meta:
        abstract = True

    def pre_save(self):
        if not self.email: self.email = self.signatory_email
        if not self.phone: self.phone = self.signatory_phone
    
    def post_save(self):
        self.update_documents()

    def update_documents(self):
        if self.property_change("role"):
            for doc in self.transaction.transaction_to_document.filter(to_sign=True):
                doc.save()

    def add_signatory_id_to_cache(self):
        self.signatory.add_cache(self.transation.backend, {"id": self.signatory_id})

    @property
    def follow_model(self):
        from mighty.functions import get_model
        label, model = conf.signatory_relation.split(".")
        return get_model(label, model)

    def getattr_signatory(self, attr):
        if hasattr(self.signatory, attr):
            return getattr(self.signatory, attr)
        raise NotImplementedError("Signatory need attribute : %s" % attr)

    @property
    def locations(self):
        return self.signatory_to_location.all()
        

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
