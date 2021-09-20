from django import forms
from mighty.models import PaymentMethod
from mighty.applications.shop.forms.widgets import IbanInput, BicInput

class IbanForm(forms.ModelForm):
    form_method = forms.CharField(required=False)
    iban = forms.CharField(widget=IbanInput(), required=True)
    bic = forms.CharField(widget=BicInput(), required=True)

    class Meta:
        model = PaymentMethod
        fields = ('owner', 'iban', 'bic')
