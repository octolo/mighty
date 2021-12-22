from django.db import models
from django.utils import timezone

from mighty.models.base import Base
from mighty.applications.shop import choices as _c
from mighty.applications.shop.decorators import GroupOrUser

from mighty.applications.shop.models.items.subscription.bill import Bill
from mighty.applications.shop.models.items.subscription.service import Service
from mighty.applications.shop.models.items.subscription.pricedatepaid import PriceDatePaid

@GroupOrUser(related_name="group_subscription", on_delete=models.SET_NULL, null=True, blank=True)
class Subscription(Base, Bill, Service, PriceDatePaid):
    offer = models.ForeignKey('mighty.Offer', on_delete=models.CASCADE, related_name='offer_subscription')
    bill = models.ForeignKey('mighty.Bill', on_delete=models.SET_NULL, related_name='bill_subscription', blank=True, null=True, editable=False)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True, related_name='method_subscription')
    discount = models.ManyToManyField('mighty.Discount', blank=True, related_name='discount_subscription')
    next_paid = models.DateField(blank=True, null=True, editable=False)
    date_start = models.DateField(blank=True, null=True, editable=False)
    date_end = models.DateField(blank=True, null=True, editable=False)
    coin = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    advance = models.PositiveIntegerField(default=0)
    frequency = models.CharField(max_length=255, choices=_c.FREQUENCIES, default=_c.MONTH)
    is_active = models.BooleanField(default=False)
    status = models.CharField(max_length=255, choices=_c.SUB_STATUS, default=_c.PREPARATION, )

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_start', 'next_paid']

    def __str__(self):
        return "%s - %s" % (self.offer, self.next_paid)

    @property
    def is_active(self):
        if self.offer.frequency != 'ONUSE':
            return True if self.next_paid and self.next_paid >= timezone.now().date() else False
        return self.coin > 0
 
    @property
    def subscription_usage(self):
        return self.subscription.uid if self.valid_method else False

    def pre_save(self):
        self.set_on_use_count()
        self.set_cache_service()

    #def pre_update(self):
    #    #self.update_bill()
    #    self.set_date_on_paid()

    def post_create(self):
        self.set_subscription()
        self.do_bill()