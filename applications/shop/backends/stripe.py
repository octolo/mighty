from datetime import datetime

from mighty.applications.shop import choices as _c
from mighty.applications.shop.backends import PaymentBackend
from mighty.functions import setting


class PaymentBackend(PaymentBackend):
    APIKEY = setting('STRIPE_KEY', 'pk_test_2HJblgmwriJiakxRAgSCiAiZ')
    APISECRET = setting('STRIPE_SECRET', 'sk_test_Ut8KxxgMdbQnWqfXcyYe0JiY')
    pmtypes = {'CB': 'card', 'IBAN': 'sepa_debit'}
    api_stripe = None

    # STRIPE
    @property
    def api(self):
        import stripe
        stripe.api_key = self.APISECRET
        return stripe

    # PAYMENT METHOD
    @property
    def data_cb(self):
        datepm = datetime.strptime(str(self.payment_method.date_valid), '%Y-%m-%d')
        return {
            'billing_details': {'name': str(self.payment_method.uid)},
            'type': 'card',
            'card': {
                'number': self.payment_method.cb,
                'exp_month': datepm.month,
                'exp_year': datepm.year,
                'cvc': self.payment_method.cvc}}

    @property
    def data_iban(self):
        return {
            'billing_details': {'name': str(self.payment_method.uid), 'email': 'dev@octolo.tech'},
            'type': 'sepa_debit',
            'sepa_debit': {
                'iban': self.payment_method.iban}}

    def add_pm(self):
        self.payment_method.cache = self.add_payment_method()
        customer = self.get_or_create_customer(self.payment_method.cache)
        self.payment_method.service_id = self.payment_method.cache['id']
        self.payment_method.cache['customer'] = customer['id']
        self.payment_method.save()

    def get_or_create_customer(self, pm):
        if pm.get('customer'):
            return self.api.Customer.retrieve(pm['customer'])
        return self.api.Customer.create(payment_method=pm['id'], description=self.group)

    def add_payment_method(self, force=False):
        if not force and self.payment_method.service_id:
            return self.api.PaymentMethod.retrieve(self.payment_method.service_id)
        data_pm = getattr(self, f'data_{self.form_method.lower()}')
        self.logger.info(data_pm)
        return self.api.PaymentMethod.create(**data_pm)

    def check_pm_status(self):
        raise NotImplementedError('Subclasses should implement check_pm_status(self)')

    @property
    def pmtype(self):
        if self.payment_method.form_method in self.pmtypes:
            return self.pmtypes[self.payment_method.form_method]
        return self.payment_method.form_method.lower()

    # TO CHARGE
    @property
    def data_bill(self):
        return {
            'amount': round(self.bill.end_amount * 100),
            'currency': 'eur',
            'payment_method': self.payment_method.service_id,
            'description': self.bill.follow_id,
            'payment_method_types': [self.pmtype],
            'customer': self.payment_method.cache['customer'],
            'mandate_data': {
                'customer_acceptance': {
                    'type': 'offline',
                }
            },
            'confirm': True,
            'return_url': self.bill_return_url,
        }

    @property
    def is_paid_success(self):
        return self.bill.cache['status'] == 'succeeded'

    @property
    def payment_id(self):
        return self.bill.payment_id

    def to_charge(self):
        return self.create_or_retry_payment()

    def create_or_retry_payment(self):
        if self.payment_id:
            charge = self.api.PaymentIntent.retrieve(self.payment_id)
            if charge.status not in {'processing', 'canceled', 'succeeded'}:
                self.bill.add_cache('payment_method', self.add_payment_method(True))
                return self.api.PaymentIntent.modify(self.payment_id, **self.data_bill)
            return charge
        return self.api.PaymentIntent.create(**self.data_bill)
        # invoice = self.set_charge()
        # self.bill.payment_id = invoice.id
        # self.bill.add_cache[self.backend] = invoice
        # self.bill.backend = self.backend
        # self.bill.save()
        # return True

    @property
    def pmtype(self):
        if self.payment_method.form_method in self.pmtypes:
            return self.pmtypes[self.payment_method.form_method]
        return self.payment_method.form_method.lower()

    def on_paid_failed(self):
        if self.bill.cache['status'] == 'requires_source_action':
            need_action = self.bill.cache['next_action']['type']
            if need_action == 'redirect_to_url':
                self.bill.need_action = _c.NEED_ACTON_URL
                self.bill.action = self.bill.cache['next_action'][need_action]['url']

    def collect_status(self):
        self.bill.status = _c.NOTHING

    def check_bill_status(self):
        self.bill.cache = self.api.PaymentIntent.retrieve(self.payment_id)
        self.collect_status()
        self.bill.save()
