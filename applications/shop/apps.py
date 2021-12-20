from django.apps import AppConfig
from django.conf import settings
from mighty.functions import setting
from mighty import over_config

class Config:
    group = setting('PAYMENT_GROUP', 'auth.Group')
    method = setting('PAYMENT_METHOD', 'mighty.PaymentMethod')
    subscription_for = setting('SUBSCRIPTION_FOR', 'group')
    invoice_backend = setting('INVOICE_BACKEND', 'mighty.applications.shop.backends.stripe.PaymentBackend')
    invoice_template = setting('INVOICE_TEMPLATE', 'shop/invoice.html')
    bill_return_url = "http://%(domain)s/%(group)s/%(bill)s/"
    bill_webhook_url = "http://%(domain)s/wh/%(group)s/%(bill)s/"
    sub_return_url = "http://%(domain)s/%(group)s/%(subscription)s/"
    sub_webhook_url = "http://%(domain)s/wh/%(group)s/%(subscription)s/"
    bill_unique_together = ("group", "date_payment", "numero")


    class bank_card_conf:
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

    class sepa_conf:
        basic_sepas = [
            {"iban": "FR1420041010050500013M02606", "status": "succeeded"},
            {"iban": "FR3020041010050500013M02609", "status": "succeeded3"},
            {"iban": "FR8420041010050500013M02607", "status": "requires_payment_method"},
            {"iban": "FR7920041010050500013M02600", "status": "requires_payment_method3"},
            {"iban": "FR5720041010050500013M02608", "status": "succeededwlit"},
            {"iban": "AT611904300234573201", "status": "succeeded", },
            {"iban": "AT321904300235473204", "status": "succeeded3", },
            {"iban": "AT861904300235473202", "status": "requires_payment_method", },
            {"iban": "AT051904300235473205", "status": "requires_payment_method3", },
            {"iban": "AT591904300235473203", "status": "succeededwlit", },
        ]

if hasattr(settings, 'SHOP'): over_config(Config, settings.SHOP)
class ShopConfig(AppConfig, Config):
    name = 'mighty.applications.shop'

    def ready(self):
        from . import signals

def cards_test():
    bc = [c["number"] for c in ShopConfig.bank_card_conf.basic_cards]+[
        c["number"] for c in ShopConfig.bank_card_conf.cards_3ds]
    return bc

def sepas_test():
    return [s["iban"] for s in ShopConfig.sepa_conf.basic_sepas]