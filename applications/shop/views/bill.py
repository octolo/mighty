from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import Context, Template

from mighty.views import PDFView
from mighty.models import Bill

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