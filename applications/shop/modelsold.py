from datetime import timedelta

from django.db import models
from django.utils import timezone
from schwifty import BIC, IBAN

from mighty.applications.shop import choices, generate_code_type
from mighty.applications.shop.apps import ShopConfig
from mighty.apps import MightyConfig
from mighty.models.base import Base


class Service(Base):
    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=50, default=generate_code_type, unique=True
    )

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return f'{self.name}({self.code})'


class Offer(Base):
    name = models.CharField(max_length=255)
    frequency = models.CharField(
        max_length=255, choices=choices.FREQUENCIES, default='ONUSE'
    )
    duration = models.DurationField(blank=True, null=True, editable=False)
    price = models.FloatField()
    service = models.ManyToManyField(
        'mighty.Service', blank=True, related_name='service_offer'
    )
    price_tenant = models.FloatField(default=0.0)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_frequency_display()})'


class Subscription(Base):
    group = models.ForeignKey(
        ShopConfig.group,
        on_delete=models.CASCADE,
        related_name='group_subscription',
    )
    offer = models.ForeignKey(
        'mighty.Offer',
        on_delete=models.CASCADE,
        related_name='offer_subscription',
    )
    bill = models.ForeignKey(
        'mighty.Bill',
        on_delete=models.SET_NULL,
        related_name='bill_subscription',
        blank=True,
        null=True,
        editable=False,
    )
    discount = models.ManyToManyField(
        'mighty.Discount', blank=True, related_name='discount_subscription'
    )
    next_paid = models.DateField(blank=True, null=True, editable=False)
    date_start = models.DateField(blank=True, null=True, editable=False)
    date_end = models.DateField(blank=True, null=True, editable=False)
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

    @property
    def price(self):
        return self.offer.price

    @property
    def price_tenant(self):
        return self.offer.price_tenant * self.group.nbr_tenant

    def do_bill(self):
        amount = self.price + self.price_tenant
        for disc in self.discount.filter(date_end__lt=timezone.now).order_by(
            '-amount'
        ):
            if disc.amount and disc.is_percent:
                amount -= amount * (disc.amount / 100)
            elif disc.amount:
                amount -= disc.amount
        self.subscription_bill.create(amount=amount, group=self.group)

    def set_date_duration(self):
        pass

    @property
    def get_date_month(self):
        return self.next_paid + timedelta(days=30)

    @property
    def get_date_year(self):
        return self.next_paid + timedelta(days=MightyConfig.days_in_year)

    @property
    def get_date_oneshot(self):
        return timezone.now

    def set_date_by_duration(self):
        pass

    def should_bill(self):
        pass

    def set_date_by_frequency(self):
        self.next_paid = (
            getattr(self, f'get_date_{self.frequency.lower()}')
            if self.next_paid
            else timezone.now
        )

    def set_date_on_paid(self):
        if self.offer.duration:
            self.set_date_by_duration()
        else:
            self.set_date_by_frequency()
        # if self.is_paid:
        #    now = timezone.now
        #    self.date_start = now
        #    if self.offer.duration:
        #        self.date_end = now + self.offer.duration

    def set_on_use_count(self):
        self.one_use_count = self.offer.frequency == 'ONUSE'

    def set_subscription(self):
        if hasattr(self.group, 'subscription'):
            self.group.subscription = self
            self.group.save()

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


class Bill(Base):
    group = models.ForeignKey(
        ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True
    )
    amount = models.FloatField()
    date_payment = models.DateField(editable=False)
    paid = models.BooleanField(default=False, editable=False)
    payment_id = models.CharField(
        max_length=255, blank=True, null=True, editable=False
    )
    subscription = models.ForeignKey(
        'mighty.Subscription',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subscription_bill',
        editable=False,
    )
    method = models.ForeignKey(
        'mighty.PaymentMethod',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='method_bill',
        editable=False,
    )

    class Meta(Base.Meta):
        abstract = True


class Discount(Base):
    code = models.CharField(
        max_length=50, default=generate_code_type, unique=True
    )
    amount = models.FloatField()
    is_percent = models.BooleanField(default=False)
    date_end = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    @property
    def is_valid(self):
        if self.date_end:
            return self.date_end >= timezone.now
        return True


class PaymentMethod(Base):
    group = models.ForeignKey(
        ShopConfig.group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payment_method',
    )
    form_method = models.CharField(
        max_length=4, choices=choices.PAYMETHOD, default='CB'
    )

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

    def sum_digits(self):
        if self < 10:
            return self
        return (self % 10) + (self // 10)

    def validate_luhn(self):
        self = self[::-1]
        self = [int(x) for x in self]
        doubled_second_digit_list = []
        digits = list(enumerate(self, start=1))
        for index, digit in digits:
            if index % 2 == 0:
                doubled_second_digit_list.append(digit * 2)
            else:
                doubled_second_digit_list.append(digit)
        doubled_second_digit_list = [
            sum_digits(x) for x in doubled_second_digit_list
        ]
        sum_of_digits = sum(doubled_second_digit_list)
        return sum_of_digits % 10 == 0

    @property
    def is_valid_cb(self):
        if self.date_cb:
            return self.validate_luhn(self.cb)
        return False

    @property
    def is_valid(self):
        if self.form_method == 'IBAN':
            return self.is_valid_iban and self.is_valid_bic
        return self.is_valid_cb

    @property
    def cb_month(self):
        return self.date_cb.month

    @property
    def cb_year(self):
        return self.date_cb.year
