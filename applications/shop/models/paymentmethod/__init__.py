from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop import generate_code_type, choices, translates as _
from mighty.applications.shop.decorators import GroupOrUser

from mighty.applications.shop.models.paymentmethod.backend import BackendModel
from mighty.applications.shop.models.paymentmethod.iban import IbanModel
from mighty.applications.shop.models.paymentmethod.cb import CBModel
from mighty.applications.shop.models.paymentmethod.valid import PMValid


from dateutil.relativedelta import relativedelta
import datetime, re

@GroupOrUser(related_name="payment_method", on_delete=models.SET_NULL, null=True, blank=True)
class PaymentMethod(Base, IbanModel, CBModel, PMValid, BackendModel):
    owner = models.CharField(_.owner, max_length=255, blank=True, null=True, help_text="Owner")
    form_method = models.CharField(_.form_method, max_length=17, choices=choices.PAYMETHOD, default="CB")
    date_valid = models.DateField(_.date_valid, blank=True, null=True, help_text="Expire date")
    signature = models.TextField(_.signature, blank=True, null=True)

    # IBAN
    iban = models.CharField(_.iban, max_length=34, blank=True, null=True, help_text="IBAN")
    bic = models.CharField(_.bic, max_length=12, blank=True, null=True, help_text="BIC")

    # CB
    cb = models.CharField(_.card_number, max_length=16, blank=True, null=True, help_text=_.card_number)
    cvc = models.CharField(max_length=4, blank=True, null=True, help_text="CVC")
    month = models.DateField(blank=True, null=True)
    year = models.DateField(blank=True, null=True)

    # SERVICE
    backend = models.CharField(max_length=255, editable=False)
    service_id = models.CharField(max_length=255, editable=False)
    service_detail = models.TextField(editable=False)
    default = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    def __str__(self):
        return "%s - %s" % (self.group_or_user, getattr(self, "str_%s" % self.form_method.lower()))

    @property
    def masked(self):
        return getattr(self, "mask_%s" % self.form_method.lower())

    def qs_default(self):
        qs = type(self).objects
        return qs.filter(group=self.group) if hasattr(self, 'group') else qs.filter(user=self.user)

    def has_default(self):
        return self.qs_default().exists()

    def pre_set_default(self):
        if not self.default and not self.has_default():
            self.default = True

    def set_has_default(self):
        self.qs_default.update(default=False)
        self.default = True
        self.save()

    def clean(self):
        self.check_validity()
        self.valid_backend()

    def pre_save(self):
        self.check_validity()
        self.pre_set_default()
