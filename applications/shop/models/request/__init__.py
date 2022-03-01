from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from mighty.models.base import Base
from mighty.fields import JSONField
from mighty.apps import MightyConfig as conf
from mighty.applications.shop import choices as _c
from mighty.applications.shop.models.paymentmethod import PaymentMethod

UserModel = get_user_model()
class SubscriptionRequest(PaymentMethod):
    offer = models.ForeignKey("mighty.Offer", on_delete=models.SET_NULL, blank=True, null=True, related_name="subrequest_offer")
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="subrequest_user")
    frequency = models.CharField(max_length=255, choices=_c.FREQUENCIES, default=_c.MONTH)
    data = JSONField(blank=True, null=True)

    class Meta(PaymentMethod.Meta):
        abstract = True
        ordering = ['user', 'offer']

    def __str__(self):
        return "%s (%s)" % (self.user, self.offer)

    @property
    def webhook_url(self):
        return reverse("wbh-subscription-request", self.uid)
