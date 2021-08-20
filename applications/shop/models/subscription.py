from django.db import models
from django.utils import timezone
from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop.apps import ShopConfig
from mighty.applications.shop import generate_code_type
from datetime import timedelta

class Discount(Base):
    code = models.CharField(max_length=50, default=generate_code_type, unique=True)
    amount = models.FloatField()
    is_percent = models.BooleanField(default=False)
    date_end = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    @property
    def is_valid(self):
        if self.date_end:
            return (self.date_end >= timezone.now)
        return True

class Subscription(Base):
    if ShopConfig.subscription_for == 'group':
        group = models.ForeignKey(ShopConfig.group, on_delete=models.CASCADE, related_name='group_subscription')
    else:
        from django.contrib.auth import get_user_model
        user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_subscription')
    offer = models.ForeignKey('mighty.Offer', on_delete=models.CASCADE, related_name='offer_subscription')
    bill = models.ForeignKey('mighty.Bill', on_delete=models.SET_NULL, related_name='bill_subscription', blank=True, null=True, editable=False)
    discount = models.ManyToManyField('mighty.Discount', blank=True, related_name='discount_subscription')
    next_paid = models.DateField(blank=True, null=True, editable=False)
    date_start = models.DateField(blank=True, null=True, editable=False)
    date_end = models.DateField(blank=True, null=True, editable=False)
    is_used = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_start', 'next_paid']

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

    def do_bill(self):
        amount = self.price+self.price_tenant
        for disc in self.discount.filter(date_end__lt=timezone.now).order_by('-amount'):
            if disc.amount and disc.is_percent:
                amount -= amount*(disc.amount/100)
            elif disc.amount:
                amount -= disc.amount
        self.subscription_bill.create(amount=amount, group= self.user_or_group)

    def set_date_duration(self):
        pass

    @property
    def get_date_month(self):
        return self.next_paid+timedelta(days=30)

    @property
    def get_date_year(self):
        return self.next_paid+timedelta(days=MightyConfig.days_in_year)

    @property
    def get_date_oneshot(self):
        return timezone.now

    def set_date_by_duration(self):
        pass

    def should_bill(self):
        pass

    def set_date_by_frequency(self):
        self.next_paid = getattr(self, 'get_date_%s' % self.frequency.lower()) if self.next_paid else timezone.now

    def set_date_on_paid(self):
        self.set_date_by_duration() if self.offer.duration else self.set_date_by_frequency()
        #if self.is_paid:
        #    now = timezone.now
        #    self.date_start = now
        #    if self.offer.duration:
        #        self.date_end = now + self.offer.duration

    def set_on_use_count(self):
        self.one_use_count = True if self.offer.frequency =='ONUSE' else False

    def set_subscription(self):
        if hasattr(self.user_or_group, 'subscription'):
            self.user_or_group.subscription = self
            self.user_or_group.save()

    def set_cache_service(self):
        for service in self.offer.service.all():
            self.add_cache(service.name.lower(), service.code)

    def has_service(self, service):
        return self.has_cache_field(service.lower())

    def pre_save(self):
        self.set_on_use_count()

    def pre_update(self):
        self.set_date_on_paid()
        self.set_cache_service()

    def post_save(self):
        self.should_bill()
        self.set_subscription()