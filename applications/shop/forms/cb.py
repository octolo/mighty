from mighty.applications.shop import translates as _
from mighty.applications.shop.forms.widgets import (
    CBCVCInput,
    CBDateInput,
    CBNumberInput,
)
from mighty.forms import ModelFormDescriptable
from mighty.forms.fields import CharField
from mighty.models import PaymentMethod


class CBForm(ModelFormDescriptable):
    form_method = CharField(label=_.form_method, required=False)
    cb = CharField(label=_.card_number, widget=CBNumberInput(), required=True, icon='credit-card')
    date_valid = CharField(label=_.date_valid, widget=CBDateInput(), required=True, icon='calendar-check')
    cvc = CharField(label=_.cvc, widget=CBCVCInput(), required=True, icon='sign')

    class Meta:
        model = PaymentMethod
        fields = ('owner', 'cb', 'cvc', 'date_valid')
