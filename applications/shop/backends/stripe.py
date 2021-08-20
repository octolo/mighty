from mighty.applications.shop.backends import PaymentBackend
from mighty.functions import setting
import stripe

class PaymentBackend(PaymentBackend):
    APIKEY = setting('STRIPE_KEY', 'pk_test_2HJblgmwriJiakxRAgSCiAiZ')
    APISECRET = setting('STRIPE_SECRET', 'sk_test_Ut8KxxgMdbQnWqfXcyYe0JiY')
    api = None

    def to_invoice(self):
        invoice = self.set_charge()
        self.bill.payment_id = invoice.id
        self.bill.log = invoice
        self.bill.backend = 'mighty.applications.shop.backends.stripe'
        self.bill.save()

        return True

    # STRIPE
    def get_charge(self, id_charge):
        charge = stripe.Charge.retrieve(id_charge, api_key=self.APISECRET)
        charge.save()
        return charge

    def get_api(self):
        if self.api is None:
            self.api = stripe.api_key = self.APISECRET
        return self.api

    def set_charge(self):
        charge = self.get_api().Charge.create(
            amount=self.bill.real_amount,
            currency="eur",
            source=self.payment_method.id,
            description=self.bill.id)
        return charge

    def add_pm_cb(self, obj):
        pm = stripe.PaymentMethod.create(type="card", card={"number": obj.cb, "exp_month": obj.month.month, "exp_year": obj.year.year,, "cvc": obj.cvc})
        return pm

    def add_pm_iban(self, obj):
        pm = stripe.PaymentMethod.create(type="sepa_debit",sepa_debit={"iban": obj.iban})
        return pm