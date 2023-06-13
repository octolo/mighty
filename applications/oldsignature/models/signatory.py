from django.db import models

from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.applications.signature.apps import SignatureConfig as conf
from mighty.applications.signature import choices as _c
from mighty.applications.user import translates as u_, choices as u_choices

from colorfield.fields import ColorField
import random

def generate_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

class TransactionSignatoryWithoutInfo(models.Model):
    transaction = models.ForeignKey(conf.transaction_relation, on_delete=models.CASCADE, related_name="transaction_to_signatory")
    signatory = models.ForeignKey(conf.signatory_relation, on_delete=models.SET_NULL, blank=True, null=True)
    sign_backend_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=_c.STATUS_SIGNATORY, default=_c.PREPARATION)
    mode = models.CharField(max_length=20, choices=_c.MODE_SIGNATORY, default=_c.EMAIL)
    color = ColorField(format="hexa", default=generate_random_color)

    def __str__(self):
        return "%s(%s)" % (str(self.signatory), str(self.transaction))

    class Meta:
        abstract = True

    def post_save(self):
        self.update_documents()
        self.transaction.save()

    def post_delete(self):
        for doc in self._unmodified.transaction.transaction_to_document.all():
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
    def signatory_denomination(self):
        return self.getattr_signatory("signatory_denomination")
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

class TransactionSignatoryWithInfo(TransactionSignatoryWithoutInfo):
    fullname = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    denomination = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(u_.gender, max_length=1, choices=u_choices.GENDER, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        abstract = True

    def pre_save(self):
        if not self.fullname: self.fullname = self.signatory_fullname
        if not self.first_name: self.first_name = self.signatory_first_name
        if not self.last_name: self.last_name = self.signatory_last_name
        if not self.denomination: self.denomination = self.signatory_denomination
        if not self.email: self.email = self.signatory_email
        if not self.phone: self.phone = self.signatory_phone
        if not self.email and self.phone: self.mode = _c.SMS
