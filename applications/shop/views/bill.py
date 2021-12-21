from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import Context, Template

from mighty.views import PDFView, DetailView, ListView
from mighty.models import Bill

@method_decorator(login_required, name='dispatch')
class BillPDF(PDFView):
    model = Bill
    slug_field = 'object_id'
    slug_url_kwarg = 'object_id'
    pk_url_kwarg = "object_id"
    in_browser = True

    def get_context_data(self, **kwargs):
        return Context(self.get_object().bill_pdf_context)

    def get_pdf_name(self):
        return self.get_object().bill_pdf_name

    def get_template(self, context):
        return Template(self.bill_content_pdf).render(context)

@method_decorator(login_required, name='dispatch')
class BillList(ListView):
    model = Bill

    def get_context_data(self, **kwargs):
        return [{
            "uid": bill.uid,
            "end_amount": bill.end_amount,
            "date_payment": bill.date_payment,
            "paid": bill.paid,
            "subscription": str(bill.subscription),
            "method": str(bill.method.get_form_method_display()),
            "end_discount": bill.end_discount,
            "need_action": bill.need_action,
            "action": bill.action,
            "items": bill.items_list,
            "name": bill.name,
        } for bill in self.get_queryset()]

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs, safe=False)

class BillReturnURL(DetailView):
    pk_url_kwarg = 'payment_id'
    