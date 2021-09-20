from django import forms
from mighty.models import PaymentMethod
from mighty.applications.shop.forms.widgets import CBNumberInput, CBCVCInput, CBDateInput

class CBForm(forms.ModelForm):
    form_method = forms.CharField(required=False)
    cb = forms.CharField(widget=CBNumberInput(), required=True)
    date_valid = forms.CharField(widget=CBDateInput(), required=True)

    class Meta:
        model = PaymentMethod
        fields = ('owner', 'cb', 'cvc', 'date_valid')
