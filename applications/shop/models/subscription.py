from django.db import models

from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop.apps import ShopConfig
from mighty.applications.shop import generate_code_type

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

class Subscription(Base):
    if ShopConfig.subscription_for == 'group':
        group = models.ForeignKey(ShopConfig.group, on_delete=models.CASCADE, related_name='group_subscription')
    else:
        from django.contrib.auth import get_user_model
        user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_subscription')
    offer = models.ForeignKey('mighty.Offer', on_delete=models.CASCADE, related_name='offer_subscription')
    bill = models.ForeignKey('mighty.Bill', on_delete=models.SET_NULL, related_name='bill_subscription', blank=True, null=True, editable=False)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True, related_name='method_subscription')
    discount = models.ManyToManyField('mighty.Discount', blank=True, related_name='discount_subscription')
    next_paid = models.DateField(blank=True, null=True, editable=False)
    date_start = models.DateField(blank=True, null=True, editable=False)
    date_end = models.DateField(blank=True, null=True, editable=False)
    is_used = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_start', 'next_paid']

    def __str__(self):
        return "%s - %s" % (self.offer, self.next_paid)

    @property
    def user_or_group(self):
        return self.group if ShopConfig.subscription_for == 'group' else self.user

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
        return self.offer.price_tenant*self.user_or_group.nbr_tenant

    @property
    def should_bill(self):
        if self.method:
            print('ok')
            if not self.bill:
                self.next_paid = date.today()
            if self.offer.frequency != 'ONUSE':
                return True if not self.next_paid or self.next_paid <= date.today() else False

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
            bill = self.subscription_bill.create(amount=self.price_full, group=self.user_or_group, subscription=self, method=self.method)
            bill.discount.add(*self.discount.filter(date_end__gt=datetime.now()).order_by('-amount'))
            self.bill = bill
            self.save()


    def update_bill(self):
        if not self.bill.paid:
            self.bill.method = self.method
            self.bill.discount.add(*self.discount.filter(date_end__gt=datetime.now()).order_by('-amount'))
            self.bill.del_cache('payment_method')
            self.bill.save()

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
        if hasattr(self.user_or_group, 'subscription'):
            self.user_or_group.subscription = self
            self.user_or_group.save()

    def set_cache_service(self):
        for service in self.offer.service.all():
            self.add_cache(service.name.lower(), service.code)


    # On Save
    def pre_save(self):
        self.set_on_use_count()

    def pre_update(self):
        self.update_bill()
        self.set_date_on_paid()
        self.set_cache_service()

    def post_save(self):
        self.set_subscription()