from django.db import models
from django.utils.module_loading import import_string
from django.utils.text import get_valid_filename

from mighty.models.base import Base
from mighty.applications.shop.apps import ShopConfig
from mighty.applications.shop import translates as _
from mighty.applications.shop import choices as _c
from mighty.applications.shop.decorators import GroupOrUser

from mighty.applications.shop.models.bill.pdf import PDFModel
from mighty.applications.shop.models.bill.charge import ChargeModel

@GroupOrUser(related_name="group_bill", on_delete=models.SET_NULL, null=True, blank=True)
class Bill(Base, PDFModel, ChargeModel):
    amount = models.FloatField(blank=True, null=True)
    end_amount = models.FloatField(blank=True, null=True)
    date_payment = models.DateTimeField(blank=True, null=True, editable=False)
    paid = models.BooleanField(default=False, editable=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True, editable=False, unique=True)
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True, related_name='subscription_bill', editable=False)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True, related_name='method_bill', editable=False)
    discount = models.ManyToManyField('mighty.Discount', blank=True, related_name='discount_bill')
    end_discount = models.FloatField(blank=True, null=True)
    backend = models.CharField(max_length=255, blank=True, null=True, editable=False)
    status = models.CharField(max_length=25, choices=_c.BILL_STATUS, default=_c.NOTHING)
    action = models.TextField(blank=True, null=True, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    items = models.TextField(blank=True, null=True)
    
    class Meta(Base.Meta):
        abstract = True

    def __str__(self):
        return "%s - %s" % (self.group, self.subscription)

    @property
    def offer(self):
        return self.subscription.offer

    @property
    def items_list(self):
        return [item.split(":") for item in self.items.splitlines()] if self.items else []

    @property
    def follow_id(self):
        return "msbID_%s.%s" % (self.uid, self.pk)

    def calcul_discount(self):
        amount = self.amount
        amount -= sum([discount.amount for discount in self.discount.filter(is_percent=False)])
        for discount in self.discount.filter(is_percent=True).order_by('-amount'):
            amount -= (amount/100*discount.amount)
        self.end_amount = round(amount, 2)
        self.end_discount = round(self.amount-self.end_amount, 2)

    def pre_save(self):
        if self.payment_id:
            self.check_bill_status()

    def pre_update(self):
        self.calcul_discount()
        if self.status == _c.CHARGE:
            self.to_charge()
