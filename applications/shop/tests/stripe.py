from django.test import TestCase

class StripConfTest:
    cards = [
        { "number": "4242424242424242", "card": "Visa", },
        { "number": "4000056655665556", "card": "Visa (débit)", },
        { "number": "5555555555554444", "card": "Mastercard", },
        { "number": "2223003122003222", "card": "Mastercard (série 2)", },
        { "number": "5200828282828210", "card": "Mastercard (débit)", },
        { "number": "5105105105105100", "card": "Mastercard (prépayée)", },
        { "number": "378282246310005", "card": "American Express", },
        { "number": "371449635398431", "card": "American Express", },
        { "number": "6011111111111117", "card": "Discover", },
        { "number": "6011000990139424", "card": "Discover", },
        { "number": "3056930009020004", "card": "Diners Club", },
        { "number": "36227206271667", "card": "Diners Club (carte à 14 chiffres)", },
        { "number": "3566002020360505", "card": "JCB", },
        { "number": "6200000000000005", "card": "UnionPay", },
    ]

# Create your tests here.
class StripTestCase(TestCase):
    def setUp(self):
        Animal.objects.create(name="lion", sound="roar")
        Animal.objects.create(name="cat", sound="meow")