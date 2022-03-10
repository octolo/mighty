from mighty.views.form import FormDescView
from mighty.applications.shop.forms import PaymentMethodForm, FrequencyForm

class PaymentMethodFormDescView(FormDescView):
    form = PaymentMethodForm

class FrequencyFormDescView(FormDescView):
    form = FrequencyForm
