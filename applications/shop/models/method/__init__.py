from django.db import models

from mighty.applications.shop.decorators import GroupOrUser
from mighty.applications.shop.models.paymentmethod import PaymentMethod


@GroupOrUser(
    related_name='payment_method',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
)
class PaymentMethod(PaymentMethod):
    class Meta(PaymentMethod.Meta):
        abstract = True
        ordering = ['date_create']
