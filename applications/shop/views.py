from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import Context, Template
from django.http import JsonResponse

from mighty.views import TemplateView, ExportView, PDFView
from mighty.filters import FiltersManager, Foxid
from mighty.models import Subscription, Bill
from mighty.applications.shop import translates as _
from schwifty import IBAN


@method_decorator(login_required, name='dispatch')
class ShopExports(TemplateView):
    template_name = "admin/shop_exports.html"

@method_decorator(login_required, name='dispatch')
class ShopExport(ExportView):
    model = Subscription
    queryset = Subscription.objects.all()
    fields = ['group', 'amount']

@method_decorator(login_required, name='dispatch')
class ShopInvoicePDF(PDFView):
    model = Bill
    slug_field = 'object_id'
    slug_url_kwarg = 'object_id'
    in_browser = True


    def get_context_data(self, **kwargs):
        return Context(self.get_object().bill_pdf_context)

    def get_pdf_name(self):
        return self.get_object().bill_pdf_name

    def get_template(self, context):
        return Template(self.bill_content_pdf).render(context)

@method_decorator(login_required, name='dispatch')
class BicCalculJSON(TemplateView):
    test_field = "iban"

    def get_iban(self):
        return self.request.GET.get(self.test_field)

    def check_data(self):
        newiban = self.get_iban()
        if newiban:
            newiban = IBAN(newiban).bic
            if newiban:
                return {"bic": str(newiban.bic)}
            return { "code": "002", "error": _.error_bic_empty }
        return { "code": "001", "error": _.error_iban_empty }

    def get(self, request, format=None):
        return JsonResponse(self.check_data())