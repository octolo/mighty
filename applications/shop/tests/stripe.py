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
            GroupModel = get_model(group[0], group[1]).objects.first()
        else:
            return get_user_model().objects.first()

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
            print('pm: %s' % self.payment_method)
            self.create_subscription()
            print('sub: %s' % self.subscription)
            self.bill = self.subscription.do_bill()
            print('bill: %s' % self.bill)
            self.bill.to_charge()
            print('paid: %s' % self.bill.paid)
            self.assertEqual(self.bill.paid, True)

    def test_basic_cards_date_ko(self):
        print('-- Basic cards date ko --')
        now = datetime.today() - relativedelta(months=12)
        for cb in StripeConfTest.basic_cards:
            self.payment_method = PaymentMethod(cb=cb['number'], cvc=cb['cvc'], month=now, year=now)
            self.set_group_or_user = self.get_group_or_user()
            self.payment_method.save()
            print('pm: %s' % self.payment_method)
            self.create_subscription()
            print('sub: %s' % self.subscription)
            self.bill = self.subscription.do_bill()
            print('bill: %s' % self.bill)
            try:
                self.bill.to_charge()
            except Exception as e:
                print(str(e))
            print('paid: %s' % self.bill.paid)
            self.assertEqual(self.bill.paid, False)

    def test_3ds_cards_date_ok(self):
        print('-- Basic cards date ok --')
        now = datetime.today() + relativedelta(months=1)
        for cb in ShopConfig.bank_card_conf.cards_3ds:
            self.payment_method = PaymentMethod(cb=cb['number'], cvc=cb['cvc'], month=now, year=now)
            self.set_group_or_user = self.get_group_or_user()
            self.payment_method.save()
            print('pm: %s' % self.payment_method)
            self.create_subscription()
            print('sub: %s' % self.subscription)
            self.bill = self.subscription.do_bill()
            print('bill: %s' % self.bill)
            try:
                self.bill.to_charge()
            except Exception as e:
                print(str(e))
            print('paid: %s' % self.bill.paid)
