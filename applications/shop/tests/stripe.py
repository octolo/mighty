from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase

from mighty.applications.shop.apps import ShopConfig
from mighty.functions import get_model
from mighty.models import Offer, PaymentMethod, Subscription


class StripeConfTest:
    pass


class StripeTestCase(TestCase):
    offer = None
    subscription = None
    payment_method = None
    bill = None

    def get_group_or_user(self):
        if ShopConfig.subscription_for == 'group':
            group = ShopConfig.group.split('.')
            get_model(group[0], group[1]).objects.first()
        else:
            return get_user_model().objects.first()
        return None

    def create_offer(self):
        self.offer = Offer(name='Month 9.90€', price=999, price_tenant=199)
        self.offer.save()

    def create_subscription(self):
        self.subscription = Subscription(offer=self.offer, method=self.payment_method)
        self.subscription.save()

    def setUp(self):
        print('\n')
        self.create_offer()

    def test_basic_cards_date_ok(self):
        print('-- Basic cards date ok --')
        now = datetime.today() + relativedelta(months=1)
        for cb in ShopConfig.bank_card_conf.basic_cards:
            self.payment_method = PaymentMethod(cb=cb['number'], cvc=cb['cvc'], month=now, year=now)
            self.set_group_or_user = self.get_group_or_user()
            self.payment_method.save()
            print(f'pm: {self.payment_method}')
            self.create_subscription()
            print(f'sub: {self.subscription}')
            self.bill = self.subscription.do_bill()
            print(f'bill: {self.bill}')
            self.bill.to_charge()
            print(f'paid: {self.bill.paid}')
            assert self.bill.paid is True

    def test_basic_cards_date_ko(self):
        print('-- Basic cards date ko --')
        now = datetime.today() - relativedelta(months=12)
        for cb in StripeConfTest.basic_cards:
            self.payment_method = PaymentMethod(cb=cb['number'], cvc=cb['cvc'], month=now, year=now)
            self.set_group_or_user = self.get_group_or_user()
            self.payment_method.save()
            print(f'pm: {self.payment_method}')
            self.create_subscription()
            print(f'sub: {self.subscription}')
            self.bill = self.subscription.do_bill()
            print(f'bill: {self.bill}')
            try:
                self.bill.to_charge()
            except Exception as e:
                print(str(e))
            print(f'paid: {self.bill.paid}')
            assert self.bill.paid is False

    def test_3ds_cards_date_ok(self):
        print('-- Basic cards date ok --')
        now = datetime.today() + relativedelta(months=1)
        for cb in ShopConfig.bank_card_conf.cards_3ds:
            self.payment_method = PaymentMethod(cb=cb['number'], cvc=cb['cvc'], month=now, year=now)
            self.set_group_or_user = self.get_group_or_user()
            self.payment_method.save()
            print(f'pm: {self.payment_method}')
            self.create_subscription()
            print(f'sub: {self.subscription}')
            self.bill = self.subscription.do_bill()
            print(f'bill: {self.bill}')
            try:
                self.bill.to_charge()
            except Exception as e:
                print(str(e))
            print(f'paid: {self.bill.paid}')
