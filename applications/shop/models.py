from django.db import models
from django.utils import timezone

from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop import generate_code_type, choices
from mighty.applications.shop.apps import ShopConfig

from schwifty import IBAN, BIC

class Offer(Base):
    name = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255, choices=choices.FREQUENCIES, default='ONUSE')
    duration = models.DurationField(blank=True, null=True, editable=False)
    price = models.FloatField()

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

class Subscription(Base):
    group = models.ForeignKey(ShopConfig.group, on_delete=models.CASCADE, related_name='group_subscription')
    offer = models.ForeignKey('mighty.Offer', on_delete=models.CASCADE, related_name='offer_subscription')
    next_paid = models.DateField(blank=True, null=True, editable=False)
    bill = models.ForeignKey('mighty.Bill', on_delete=models.SET_NULL, related_name='discount_subscription', blank=True, null=True, editable=False)
    discount = models.ManyToManyField('mighty.Discount', blank=True)
    date_start = models.DateField(blank=True, null=True, editable=False)
    date_end = models.DateField(blank=True, null=True, editable=False)
    amount = models.FloatField(editable=False)
    is_used = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_start', 'next_paid']

    @property
    def subscription_usage(self):
        return self.subscription.uid if self.valid_method else False

    @property
    def is_paid(self):
        return self.bill.paid if self.bill else False

    def set_date_on_paid(self):
        if self.is_paid:
            self.date_start = timezone.now
            if self.offer.duration:
                self.date_end = timezone.now + self.offer.duration

    def pre_update(self):
        self.set_date_on_paid()

class SubscriptionGroup(models.Model):
    last_subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True, related_name='last_subscription', editable=False)
    valid_method = models.PositiveIntegerField(default=0, editable=False)
    one_use_count = models.PositiveIntegerField(default=0, editable=False)

    def is_valid(self):
        return any([self.valid_subscription, self.one_use_count])

    def set_valid_method(self):
        self.valid_method = len(list(filter(True, [pm.is_valid() for pm in self.payment_method.all()])))

    def set_on_use_count(self):
        self.one_use_count = self.group_subscription.filter(frequency='ONUSE', is_used=False).count()

    def set_last_subscription(self):
        self.last_subscription = self.last_subscription.order_by('-date_start').last()

    def pre_update(self):
        self.set_last_subscription()
        self.set_valid_method()
        self.set_on_use_count()

    class Meta:
        abstract = True

class Bill(Base):
    group = models.ForeignKey(ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    date_payment = models.DateField(editable=False)
    paid = models.BooleanField(default=False, editable=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True, editable=False)
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True, related_name='subscription_bill', editable=False)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True, related_name='method_bill', editable=False)
    
    class Meta(Base.Meta):
        abstract = True

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

class PaymentMethod(Base):
    group = models.ForeignKey(ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True, related_name="payment_method")
    form_method = models.CharField(max_length=4, choices=choices.PAYMETHOD, default="CB")

    # IBAN
    iban = models.CharField(max_length=27, blank=True, null=True)
    bic = models.CharField(max_length=12, blank=True, null=True)
    cb = models.CharField(max_length=16, blank=True, null=True)
    date_cb = models.DateField(blank=True, null=True)

    # SERVICE
    backend = models.CharField(max_length=255, editable=False)
    service_id = models.CharField(max_length=255, editable=False)
    service_detail = models.TextField(editable=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    @property
    def is_valid_iban(self):
        try:
            IBAN(self.compact_iban)
            return True
        except ValueError:
            return False

    @property
    def is_valid_bic(self):
        try:
            BIC(self.bic)
            return True
        except ValueError:
            return False

    def get_cc_number():
        if len(sys.argv) < 2:
            usage()
            sys.exit(1)
        return sys.argv[1]

    def sum_digits(digit):
        if digit < 10:
            return digit
        else:
            sum = (digit % 10) + (digit // 10)
            return sum

    def validate_luhn(cc_num):
        cc_num = cc_num[::-1]
        cc_num = [int(x) for x in cc_num]
        doubled_second_digit_list = list()
        digits = list(enumerate(cc_num, start=1))
        for index, digit in digits:
            if index % 2 == 0:
                doubled_second_digit_list.append(digit * 2)
            else:
                doubled_second_digit_list.append(digit)
        doubled_second_digit_list = [sum_digits(x) for x in doubled_second_digit_list]
        sum_of_digits = sum(doubled_second_digit_list)
        return sum_of_digits % 10 == 0

    @property
    def is_valid_cb(self):
        if self.date_cb:
            return self.validate_luhn(self.cb)
        return False

    @property
    def is_valid(self):
        if self.form_method == "IBAN":
            return (self.is_valid_iban and self.is_valid_bic)
        return self.is_valid_cb

    @property        
    def cb_month(self):
        return self.date_cb.month

    @property
    def cb_year(self):
        return self.date_cb.year
