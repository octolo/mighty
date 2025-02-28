from django.forms import RadioSelect

from mighty.applications.shop.choices import FREQUENCIES_USABLE
from mighty.applications.shop.forms.cb import CBForm
from mighty.applications.shop.forms.iban import IbanForm
from mighty.applications.shop.forms.paymentmethod import PaymentMethodForm
from mighty.forms import ModelFormDescriptable
from mighty.models import Offer


class FrequencyForm(ModelFormDescriptable):
    class Meta:
        model = Offer
        fields = ('frequency',)
        widgets = {
            'frequency': RadioSelect(),
        }

    def prepare_descriptor(self, *args, **kwargs):
        self.fields['frequency'].choices = FREQUENCIES_USABLE


__all__ = (
    CBForm,
    IbanForm,
    PaymentMethodForm,
    FrequencyForm,
)
