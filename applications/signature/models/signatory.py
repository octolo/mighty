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
        if not self.email and self.phone: self.mode = _c.SMS
    
    def post_save(self):
        self.update_documents()
        self.transaction.save()

    def post_delete(self):
        for doc in self._old_self.transaction.transaction_to_document.all():
            doc.save()

    def update_documents(self):
        if self.property_change("role"):
            for doc in [doc for doc in self.transaction.transaction_to_document.all() if doc.to_sign]:
                doc.save()

    @property
    def follow_model(self):
        from mighty.functions import get_model
        label, model = conf.signatory_relation.split(".")
        return get_model(label, model)

    def getattr_signatory(self, attr, raise_error=True):
        if hasattr(self.signatory, attr):
            return getattr(self.signatory, attr)
        if raise_error:
            raise NotImplementedError("Signatory need attribute : %s" % attr)
        return None

    @property
    def locations(self):
        return self.signatory_to_location.all()

    @property
    def role(self):
        return _c.SIGNATORY if self.signatory_to_location.count() else _c.OBSERVER

    @property
    def need_to_sign(self):
        return (self.role == _c.SIGNATORY)

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
    def signatory_first_name(self):
        return self.getattr_signatory("signatory_first_name")
    @property
    def signatory_last_name(self):
        return self.getattr_signatory("signatory_last_name")
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
    @property
    def has_contact(self):
        return True if (self.has_email or self.has_phone) else False

    def add_to_transaction(self):
        self.transaction.signature_backend.add_signatory(self)