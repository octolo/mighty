from django.conf import settings
from django.utils import timezone
from mighty.apps import MightyConfig
from mighty.applications.shop.apps import ShopConfig
import logging

logger = logging.getLogger(__name__)

class PaymentBackend:
    in_error = False
    bill = None
    backend = None
    payment_method = None

    def __init__(self, bill, backend, *args, **kwargs):
        self.bill = bill
        self.backend = backend

    @property
    def return_url(self):
        url = ShopConfig.tpl_return_url % {"domain": self.domain, "group": self.bill.group, "bill": self.bill.uid}
        print(url)
        return url

    @property
    def domain(self):
        return MightyConfig.domain

    @property
    def offer(self):
        return self.bill.offer

    @property
    def billing_detail(self):
        return "%s - %s" % (self.domain, self.offer)

    # Payment Method
    @property
    def payment_method(self):
        return self.bill.method

    @property
    def form_method(self):
        return self.payment_method.form_method

    @property
    def payment_method_cache(self):
        if self.bill.has_cache_field("payment_method"):
            return self.bill.cache["payment_method"]
        return None

    def add_pm(self):
        self.bill.add_cache("payment_method", self.add_payment_method())
        self.bill.save()

    def on_paid_failed(self):
        raise NotImplementedError("Subclasses should implement on_paid_failed()")

    def add_payment_method(self, force=False):
        raise NotImplementedError("Subclasses should implement add_payment_method(self, force)")

    # Charge
    @property
    def charge(self):
        if self.bill.has_cache_field(self.backend):
            return self.bill.cache[self.backend]
        return None
    
    def try_to_charge(self):
        if not self.bill.paid:
            self.bill.add_cache(self.backend, self.to_charge())
            if self.is_paid_success:
                self.bill.paid = True
                self.bill.payment_id = self.payment_id
                self.bill.date_payment = timezone.now()
            else:
                self.on_paid_failed()
            self.bill.save()

    # To implement
    def to_charge(self):
        raise NotImplementedError("Subclasses should implement to_charge(self)")
    
    @property
    def is_paid_success(self):
        raise NotImplementedError("Subclasses should implement is_paid_success")

    @property
    def payment_id(self):
        raise NotImplementedError("Subclasses should implement payment_id")
