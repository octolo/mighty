from django import forms
from mighty.models import PaymentMethod
from mighty.forms import FormDescriptable, ModelFormDescriptable
from mighty.applications.shop.forms.widgets import CBNumberInput, CBCVCInput, CBDateInput
from mighty.applications.shop import translates as _

class CBForm(ModelFormDescriptable):
    form_method = forms.CharField(label=_.form_method, required=False)
    cb = forms.CharField(label=_.card_number, widget=CBNumberInput(), required=True)
    date_valid = forms.CharField(label=_.date_valid, widget=CBDateInput(), required=True)

    class Meta:
        model = PaymentMethod
        fields = ('owner', 'cb', 'cvc', 'date_valid')
