from django.test import TestCase
from django.contrib.auth import get_user_model

from mighty.functions import get_model
from mighty.models import Offer, Subscription, PaymentMethod, Bill
from mighty.applications.shop.apps import ShopConfig

from datetime import datetime
from dateutil.relativedelta import relativedelta

class StripeConfTest:
    basic_cards = [
        { "cvc": "123", "number": "4242424242424242", "card": "Visa", },
        { "cvc": "123", "number": "4000056655665556", "card": "Visa (débit)", },
        { "cvc": "123", "number": "5555555555554444", "card": "Mastercard", },
        { "cvc": "123", "number": "2223003122003222", "card": "Mastercard (série 2)", },
        { "cvc": "123", "number": "5200828282828210", "card": "Mastercard (débit)", },
        { "cvc": "123", "number": "5105105105105100", "card": "Mastercard (prépayée)", },
        { "cvc": "1234", "number": "378282246310005", "card": "American Express", },
        { "cvc": "1234", "number": "371449635398431", "card": "American Express", },
        # Canada, United Kingdom, and United States
        #{ "cvc": "123", "number": "6011111111111117", "card": "Discover", },
        #{ "cvc": "123", "number": "6011000990139424", "card": "Discover", },
        #{ "cvc": "123", "number": "3056930009020004", "card": "Diners Club", },
        #{ "cvc": "123", "number": "36227206271667",   "card": "Diners Club (carte à 14 chiffres)", },
        # Australia, Canada, Japan, New Zealand, and United States
        #{ "cvc": "123", "number": "3566002020360505", "card": "JCB", },
        # Australia, Canada, Hong Kong, Singapore, and United States
        #{ "cvc": "123", "number": "6200000000000005", "card": "UnionPay", },
    ]

    cards_3ds = [
        # Rules
        {"cvc": "123", "number": "4000002500003155", },
        {"cvc": "123", "number": "4000002760003184", },
        {"cvc": "123", "number": "4000008260003178", },
        {"cvc": "123", "number": "4000003800000446", },
        {"cvc": "123", "number": "4000053560000011", },
        {"cvc": "123", "number": "4000000000003220", },
        # Tokens
        {"cvc": "123", "number": "4000000000003063", },
        {"cvc": "123", "number": "4000008400001629", },
        {"cvc": "123", "number": "4000008400001280", },
        {"cvc": "123", "number": "4000000000003055", },
        {"cvc": "123", "number": "4000000000003097", },
        {"cvc": "123", "number": "4242424242424242", },
        {"cvc": "123", "number": "378282246310005", },
    ]

    sepa = [
        {"iban": "AT611904300234573201", "status": "succeeded",
        {"iban": "AT321904300235473204", "status": "succeeded3",
        {"iban": "AT861904300235473202", "status": "requires_payment_method",
        {"iban": "AT051904300235473205", "status": "requires_payment_method3",
        {"iban": "AT591904300235473203", "status": "succeededwlit",
    ]

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
        self.offer = Offer(name="Month 9.90€", price=9.99, price_tenant=1.99)
        self.offer.save()

    def create_subscription(self):
        self.subscription = Subscription(offer=self.offer, method=self.payment_method)
        self.subscription.save()

    def setUp(self):
        print('\n')
        self.create_offer()

    def test_basic_cards_date_ok(self):
        print('-- Basic cards date ok --')
        now = datetime.today()+relativedelta(months=1)
        for cb in StripeConfTest.basic_cards:
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
        now = datetime.today()-relativedelta(months=12)
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
        now = datetime.today()+relativedelta(months=1)
        for cb in StripeConfTest.cards_3ds:
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
