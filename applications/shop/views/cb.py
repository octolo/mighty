from mighty.views import FormDescView, CheckData
from mighty.applications.shop.forms import CBForm
from mighty.models import PaymentMethod
from django.core.exceptions import ValidationError

class CBFormDescView(FormDescView):
    form = CBForm

class CheckCB(CheckData):
    def get_data(self):
        return self.get_request_type()

    def check_data(self):
        pm = PaymentMethod(**self.get_data())
        pm.form_method = "CB"
        try:
            pm.check_validity()
        except ValidationError as e:
            return self.msg_errors(e)
        return self.msg_no_errors()
