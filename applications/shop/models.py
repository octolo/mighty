from django.db import models
from mighty.applications.shop import generate_code_type

class Subscription(Base):
    name = models.CharField(max_length=255, null=True, blank=True)
    frequency = models.CharField(max_length=255, choices=FREQUENCIES, default=YEAR)
    amount = models.FloatField()

    class Meta:
        abstract = True
        ordering = ['name']

class Subscribable(Base):
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True)
    last_bill = models.ForeignKey('mighty.Bill', on_delete=models.SET_NULL, blank=True, null=True)
    date_subscription = models.DateField()

    class Meta:
        abstract = True

class Bill(Base):
    amount = models.FloatField()
    discount = models.ManyToManyField('mighty.Discount', blank=True, null=True)
    date_payment = models.DateField()

class Discount(Base):
    code = models.CharField(max_length=50, default=generate_code_type, unique=True)
    amount = models.FloatField()

    class Meta:
        abstract = True
        ordering = ['date_create']

class PaymentMethod(Base):
    # IBAN
    country = models.CharField(max_length=2)
    iban_key = models.CharField(max_length=2)
    blank = models.CharField(max_length=5)
    counter = models.CharField(max_length=5)
    account = models.CharField(max_length=11)
    rib_key = models.CharField(max_length=2)

    # CB
    transmitter = models.CharField(max_length=6)
    identifier = models.CharField(max_length=9)
    authenticity = models.CharField(max_length=1)

    # SERVICE
    backend = models.CharField(max_length=255, editable=False)
    service_id = models.CharField(max_length=255, editable=False)
    service_detail = models.TextField()

    class Meta:
        abstract = True
        ordering = ['date_create']

class Payment(Base, PaymentMethod):
    bill = models.ForeignKey('mighty.Bill', on_delete=models.SET_NULL, blank=True, null=True, related_name="bill_payment")
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True)
    save_method = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['date_create']
