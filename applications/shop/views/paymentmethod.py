from mighty.applications.shop.forms import FrequencyForm, PaymentMethodForm
from mighty.views.form import FormDescView


class PaymentMethodFormDescView(FormDescView):
    form = PaymentMethodForm


class FrequencyFormDescView(FormDescView):
    form = FrequencyForm
