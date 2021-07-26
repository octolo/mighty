from django.db import models
from mighty.models.base import Base
from mighty.applications.shop.apps import ShopConfig

class Bill(Base):
    group = models.ForeignKey(ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    date_payment = models.DateField(editable=False)
    paid = models.BooleanField(default=False, editable=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True, editable=False)
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True, related_name='subscription_bill', editable=False)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True, related_name='method_bill', editable=False)
    discount = models.FloatField(default=0.0)
    
    class Meta(Base.Meta):
        abstract = True

    @property
    def real_amount(self):
        amount = self.amount - self.discount
        return 0.0 if amount < 0 else amount