from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PaymentBackend:
    in_error = False
    bill = None
    payment_method = None

    def __init__(self, bill, *args, **kwargs):
        self.bill = bill

    def add_payment_method(self):
        pm = "add_pm_%s" % self.bill.form_method.lower()
        if hasattr(self, pm):
            self.payment_method = getattr(self, pm)(self.bill.method)

    def to_invoice(self):
        raise NotImplementedError("Subclasses should implement to_invoice()")