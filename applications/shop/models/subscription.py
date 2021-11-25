from django.db import models
from django.utils import timezone

from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop import generate_code_type, choices
from mighty.applications.shop.apps import ShopConfig
from mighty.applications.shop.decorators import GroupOrUser

from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)

class Discount(Base):
    code = models.CharField(max_length=50, default=generate_code_type, unique=True)
    amount = models.FloatField()
    is_percent = models.BooleanField(default=False)
    date_end = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    def __str__(self):
        return "%s: %s (-%s %s)" % (self.code, self.date_end, self.amount, self.type_discount)

    @property
    def type_discount(self):
        return "%" if self.is_percent else "€"

    @property
    def is_valid(self):
        if self.date_end:
            return (self.date_end >= date.today())
        return True


@GroupOrUser(related_name="group_subscription", on_delete=models.SET_NULL, null=True, blank=True)
class Subscription(Base):
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
    frequency = models.CharField(max_length=255, choices=choices.FREQUENCIES, default=choices.MONTH)
    is_active = models.BooleanField(default=False)

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

    @property
    def is_paid(self):
        return self.bill.paid if self.bill else False

    @property
    def price(self):
        return self.offer.price
    
    @property
    def price_tenant(self):
        if self.group_or_user:
            return self.offer.price_tenant*self.group_or_user.nbr_tenant
        return 0

    @property
    def should_bill(self):
        if self.method:
            if not self.bill:
                self.next_paid = date.today()
            if self.offer.frequency != 'ONUSE':
                return True if not self.next_paid or self.next_paid <= date.today() else False
        return False

    @property
    def discount_amount(self):
        return self.bill.end_discount

    @property
    def price_full(self):
        return self.price+self.price_tenant

    # Charging
    def do_bill(self):
        if self.should_bill:
            logger.info('generate a new bill for subscription: %s' % self.pk)
            bill = self.subscription_bill.create(amount=self.price_full, group=self.group_or_user, subscription=self, method=self.method)
            bill.discount.add(*self.discount.filter(date_end__gt=datetime.now()).order_by('-amount'))
            self.bill = bill
            self.save()
        return self.bill


    def update_bill(self):
        if not self.bill.paid:
            self.bill.method = self.method
            self.bill.discount.add(*self.discount.filter(date_end__gt=datetime.now()).order_by('-amount'))
            self.bill.del_cache('payment_method')
            self.bill.save()


    def on_bill_paid(self):
        if self.offer.frequency != 'ONUSE':
            pass
        else:
            self.coin+=1
            self.save()

    # Test
    def has_service(self, service):
        return self.has_cache_field(service.lower())


    # Get DATE
    def get_date_month(self):
        return self.next_paid+relativedelta(months=1)

    def get_date_year(self):
        return self.next_paid+relativedelta(months=12)

    def get_date_oneshot(self):
        return date.today()


    # Set DATE
    def set_date_by_frequency(self):
        self.next_paid = getattr(self, 'get_date_%s' % self.offer.frequency.lower())() if self.next_paid else datetime.now

    def set_date_on_paid(self):
        self.set_date_by_duration() if self.offer.duration else self.set_date_by_frequency()


    # Set Boolean/Subscription/Service
    def set_on_use_count(self):
        self.one_use_count = True if self.offer.frequency =='ONUSE' else False

    def set_subscription(self):
        if hasattr(self.group_or_user, 'subscription'):
            self.group_or_user.subscription = self
            self.group_or_user.save()

    def set_cache_service(self):
        if self.offer:
            for service in self.offer.service.all():
                self.add_cache(service.name.lower(), service.code)

    # On Save
    def pre_save(self):
        self.set_on_use_count()
        self.set_cache_service()

    #def pre_update(self):
    #    #self.update_bill()
    #    self.set_date_on_paid()

    def post_create(self):
        self.set_subscription()
        self.do_bill()