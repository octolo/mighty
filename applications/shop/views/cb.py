from mighty.views import FormDescView, CheckData
from mighty.applications.shop.forms import CBForm
from mighty.models import PaymentMethod
from django.core.exceptions import ValidationError

class CBFormDescView(FormDescView):
    form = CBForm

class CheckCB(CheckData):
    def get_data(self):
        data = self.request.POST
        data["form_method"] = "CB"
        return data

    def check_data(self):
        pm = PaymentMethod(**self.get_data())
        try:
            pm.check_validity()
        except ValidationError as e:
            return self.msg_errors({ "code": e.code, "error": str(e.message) })
        return self.msg_no_errors()

from mighty.functions import setting

if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.views import APIView
    from rest_framework.response import Response
    
    class CheckCB(CheckCB, APIView):
        def get_data(self):
            data = self.request.data
            data["form_method"] = "CB"
            return data

        def post(self, request, format=None):
            return Response(self.check_data())