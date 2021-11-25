from mighty.applications.shop.backends import PaymentBackend
from mighty.functions import setting
from mighty.applications.shop import choices as choice
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PaymentBackend(PaymentBackend):
    APIKEY = setting('STRIPE_KEY', 'pk_test_2HJblgmwriJiakxRAgSCiAiZ')
    APISECRET = setting('STRIPE_SECRET', 'sk_test_Ut8KxxgMdbQnWqfXcyYe0JiY')
    pmtypes = { "CB": "card", "IBAN": "sepa_debit" }
    api_stripe = None

    def __init__(self, bill, backend, *args, **kwargs):
        super().__init__(bill, backend, *args, **kwargs)

    #def to_charge(self):
    #    invoice = self.set_charge()
    #    self.bill.payment_id = invoice.id
    #    self.bill.add_cache[self.backend] = invoice
    #    self.bill.backend = self.backend
    #    self.bill.save()
    #    return True

    @property
    def pmtype(self):
        if self.payment_method.form_method in self.pmtypes:
            return self.pmtypes[self.payment_method.form_method]
        return self.payment_method.form_method.lower()

    @property
    def pm_stripe(self):
        pm = self.api.PaymentMethod.retrieve(self.payment_method_cache["id"],)

    # STRIPE
    @property
    def api(self):
        import stripe
        stripe.api_key = self.APISECRET
        return stripe

    # Charge
    @property
    def payment_id(self):
        return self.bill.payment_id

    @property
    def data_bill(self):
        return {
            "amount": int(round(self.bill.end_amount*100)),
            "currency": "eur",
            "payment_method": self.payment_method_cache["id"],
            "description": self.bill.follow_id,
            "payment_method_types": [self.pmtype]
        }

    def retry_to_charge(self):
        charge = self.api.PaymentIntent.retrieve(self.payment_id)
        if charge.status not in ["processing", "canceled", "succeeded"]:
            self.bill.add_cache("payment_method", self.add_payment_method(True))
            return self.api.PaymentIntent.modify(self.payment_id, **self.data_bill)

    def to_charge(self):
        print("ok")
        if self.charge: return self.retry_to_charge()
        return self.api.PaymentIntent.create(**self.data_bill, confirm=True, return_url=self.return_url)

    @property
    def is_paid_success(self):
        return True if self.charge["status"] == "succeeded" else False

    def on_paid_failed(self):
        if self.charge["status"] == "requires_source_action":
            need_action = self.charge["next_action"]["type"]
            if need_action == "redirect_to_url":
                self.bill.need_action = choice.NEED_ACTON_URL
                self.bill.action = self.charge["next_action"][need_action]["url"]

    def check_status(self):
        return self.api.PaymentIntent.retrieve(self.payment_id)

    # Payment Method
    @property
    def data_cb(self):
        datepm = datetime.strptime(str(self.payment_method.date_valid), "%Y-%m-%d")
        return {
            "billing_details": self.billing_details,
            "type": "card",
            "card": {
                "number": self.payment_method.cb,
                "exp_month": datepm.month,
                "exp_year": datepm.year,
                "cvc": self.payment_method.cvc}}
    
    @property
    def billing_details(self):
        return {
            "name": self.billing_detail,
        }

    @property
    def data_iban(self):
        return {
            "billing_details": self.billing_details,
            "type": "sepa_debit",
            "sepa_debit": {"iban": self.payment_method.iban}}

    def add_payment_method(self, force=False):
        if not force:
            try:
                return self.api.PaymentMethod.retrieve(self.payment_method_cache['id'])
            except Exception:
                pass
        data_pm = getattr(self, "data_%s" % self.form_method.lower())
        return self.api.PaymentMethod.create(**data_pm)
