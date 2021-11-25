from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from mighty.views import TemplateView, CheckData
from mighty.applications.shop import translates as _
from mighty.views.form import FormDescView
from mighty.applications.shop.forms import IbanForm
from mighty.models import PaymentMethod
from mighty.functions import setting
from schwifty import IBAN
import re

@method_decorator(login_required, name='dispatch')
class BicCalculJSON(TemplateView):
    test_field = "iban"

    def get_iban(self):
        return re.sub(r"\s+", "",  self.request.GET.get(self.test_field), flags=re.UNICODE)

    def check_data(self):
        newiban = self.get_iban()
        if newiban:
            try:
                newiban = IBAN(newiban)
                if newiban:
                    return {"bic": str(newiban.bic)}
                return { "code": "002", "error": _.error_bic_empty }
            except Exception as e:
                return {"code": "003", "error": str(e)}
        return { "code": "001", "error": _.error_iban_empty }

    def get(self, request, format=None):
        return JsonResponse(self.check_data())

class IbanFormDescView(FormDescView):
    form = IbanForm

class CheckIban(CheckData):
    def get_data(self):
        data = self.request.POST
        data["form_method"] = "IBAN"
        return data

    def check_data(self):
        pm = PaymentMethod(**self.get_data())
        try:
            pm.check_validity()
        except ValidationError as e:
            return self.msg_errors({ "code": e.code, "error": str(e.message) })
        return self.msg_no_errors()

if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.views import APIView
    from rest_framework.response import Response
    
    class CheckIban(CheckIban, APIView):
        def get_data(self):
            data = self.request.data
            data["form_method"] = "IBAN"
            return data

        def post(self, request, format=None):
            return Response(self.check_data())