from django import forms
from mighty.models import PaymentMethod
from mighty.forms import ModelFormDescriptable
from mighty.applications.shop.forms.widgets import IbanInput, BicInput
from mighty.forms.widgets import SignatureInput
from mighty.applications.shop import translates as _

class IbanForm(ModelFormDescriptable):
    form_method = forms.CharField(required=False)
    iban = forms.CharField(label=_.iban, widget=IbanInput(), required=True)
    bic = forms.CharField(label=_.bic, widget=BicInput(), required=True)
    signature = forms.CharField(label=_.signature, widget=SignatureInput(), required=True)

    class Meta:
        model = PaymentMethod
        fields = ('owner', 'iban', 'bic')
