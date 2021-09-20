from mighty.views.form import FormDescView
from mighty.applications.shop.forms import PaymentMethodForm

class PaymentMethodFormDescView(FormDescView):
    form = PaymentMethodForm

