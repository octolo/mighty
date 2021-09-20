from django import forms
from mighty.models import PaymentMethod
from mighty.applications.shop.forms.widgets import (
    CBNumberInput, CBCVCInput, CBDateInput,
    IbanInput, BicInput
)

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ('owner', 'iban', 'bic', 'cb', 'cvc', 'date_valid')
        widgets = {
            'cb': CBNumberInput(),
            'cvc': CBCVCInput(),
            'date_valid': CBDateInput(),
            'iban': IbanInput(),
            'bic': BicInput(),
        }