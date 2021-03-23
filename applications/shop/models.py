from django.db import models
from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop import generate_code_type, choices
from mighty.applications.shop.apps import ShopConfig

from schwifty import IBAN, BIC
import fast_luhn

class Subscription(Base):
    name = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255, choices=choices.FREQUENCIES, default='ONUSE')
    amount = models.FloatField()

    class Meta:
        abstract = True
        ordering = ['name']

class SubscriptionGroup(models.Model):
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, related_name='group_subscription', null=True, blank=True)
    next_paid = models.DateField(auto_now_add=True)
    valid_method = models.PositiveIntegerField(default=0)

    @property
    def subscription_usage(self):
        return self.subscription.uid if self.valid_method else False

    class Meta:
        abstract = True

    #def save(self, *args, **kwargs):
    #    if self.pk:
    #        self.valid_method = len(list(filter(True, [pm.is_valid() for pm in self.payment_method.all()])))

class Bill(Base):
    group = models.ForeignKey(ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    discount = models.ManyToManyField('mighty.Discount', blank=True)
    date_payment = models.DateField()
    paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True)
    
    class Meta:
        abstract = True

class Discount(Base):
    code = models.CharField(max_length=50, default=generate_code_type, unique=True)
    amount = models.FloatField()
    is_percent = models.BooleanField(default=False)
    date_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['date_create']

choices = (
    ("CB", "CB"),
    ("IBAN", "IBAN"),
)
class PaymentMethod(Base):
    group = models.ForeignKey(ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True, related_name="payment_method")
    form_method = models.CharField(max_length=4, choices=choices, default="CB")

    # IBAN
    iban = models.CharField(max_length=27, blank=True, null=True)
    bic = models.CharField(max_length=12, blank=True, null=True)
    cb = models.CharField(max_length=16, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    # SERVICE
    backend = models.CharField(max_length=255, editable=False)
    service_id = models.CharField(max_length=255, editable=False)
    service_detail = models.TextField()

    def is_valid_iban(self):
        try:
            IBAN(self.compact_iban)
            return True
        except ValueError:
            return False

    def is_valid_bic(self):
        try:
            BIC(self.bic)
            return True
        except ValueError:
            return False

    def is_valid_cb(self):
        return fast_luhn.validate(self.cb)

    def is_valid(self):
        if self.form_method == "IBAN":
            return self.is_valid_iban()
        return self.is_valid_cb()
        
    class Meta:
        abstract = True
        ordering = ['date_create']

