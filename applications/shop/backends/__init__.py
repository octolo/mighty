from django.conf import settings
from django.utils import timezone

from mighty.applications.shop.apps import ShopConfig
from mighty.backend import Backend
from mighty.applications.shop import choices as _c

class PaymentBackend(Backend):
    backend = None
    bill = None
    subscription = None
    payment_method = None
    cache_group_field = "siren"

    def __init__(self, backend, *args, **kwargs):
        self.backend = backend
        self.bill = kwargs.get("bill") if "bill" in kwargs else None
        self.payment_method = kwargs.get("payment_method") if "payment_method" in kwargs else None
        self.subscription = kwargs.get("subscription") if "subscription" in kwargs else None

    # SHORTCUTS
    @property
    def offer(self):
        return self.bill.offer

    @property
    def billing_detail(self):
        return "%s - %s" % (self.domain, self.offer)

    @property
    def form_method(self):
        return self.payment_method.form_method

    @property
    def group(self):
        if self.bill and self.bill.group:
            return self.bill.group.named_id
        elif self.subscription and self.subscription.group:
            return self.subscription.group.named_id
        return self.payment_method.group.named_id

    @property
    def cache(self):
        if self.bill and self.bill.has_cache_field(self.bill.backend):
            return self.bill.cache[self.bill.backend]
        return None

    # URLS/WEBHOOKS
    @property
    def bill_return_url(self):
        return ShopConfig.bill_return_url % {"domain": self.domain, "group": self.group, "bill": self.bill.uid}

    @property
    def bill_webhook_url(self):
        return ShopConfig.bill_webhook_url % {"domain": self.domain, "group": self.group, "bill": self.bill.uid}

    @property
    def sub_return_url(self):
        return ShopConfig.sub_return_url % {"domain": self.domain, "group": self.group, "subscription": self.subscription.uid}

    @property
    def sub_webhook_url(self):
        return ShopConfig.sub_return_url % {"domain": self.domain, "group": self.group, "subscription": self.subscription.uid}

    @property
    def payment_method_cache(self):
        if self.bill.has_cache_field("payment_method"):
            return self.bill.cache["payment_method"]
        return None

    @property
    def charge_backend(self):
        if self.bill.has_cache_field(self.backend):
            return self.bill.cache[self.backend]
        return None

    # PAYMENT METHOD
    def add_pm(self):
        self.payment_method.cache = self.add_payment_method()
        self.payment_method.save()

    def add_payment_method(self, force=False):
        raise NotImplementedError("Subclasses should implement add_payment_method(self, force)")

    def check_pm_status(self):
        raise NotImplementedError("Subclasses should implement check_pm_status(self)")

    # BILL
    def try_to_charge(self):
        if not self.bill.paid:
            self.bill.cache = self.to_charge()
            self.bill.payment_id = self.payment_id
            if self.is_paid_success:
                self.bill.paid = True
                self.bill.date_payment = timezone.now()
            else:
                self.on_paid_failed()
            self.bill.status = _c.PAID
            self.bill.save()

    @property
    def is_paid_success(self):
        raise NotImplementedError("Subclasses should implement is_paid_success")

    @property
    def payment_id(self):
        raise NotImplementedError("Subclasses should implement payment_id")

    def check_bill_status(self):
        raise NotImplementedError("Subclasses should implement check_bill_status(self)")

    def on_paid_failed(self):
        raise NotImplementedError("Subclasses should implement on_paid_failed()")

    def to_charge(self):
        raise NotImplementedError("Subclasses should implement to_charge(self)")
