
from django.http import JsonResponse

from mighty.models import Bill
from mighty.views import DetailView


class StripeCheckStatus(DetailView):
    slug_field = 'payment_id'
    slug_url_kwarg = 'payment_id'
    queryset = Bill.objects.all()
    events = [
        'payment_intent.canceled',
        'payment_intent.created',
        'payment_intent.payment_failed',
        'payment_intent.processing',
        'payment_intent.requires_action',
        'payment_intent.succeeded',
    ]

    def get_context_data(self, **kwargs):
        bill = self.get_object()
        charge = bill.check_status()
        return charge

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs, safe=False)
