from django import forms

from mighty.applications.shop.forms.widgets import (
    BicInput,
    CBCVCInput,
    CBDateInput,
    CBNumberInput,
    IbanInput,
)
from mighty.models import PaymentMethod


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
