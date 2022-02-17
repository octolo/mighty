from django.http import JsonResponse
from mighty.views import DetailView
from mighty.applications.signature import get_transaction_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

TransactionModel = get_transaction_model()
DocumentModel = TransactionModel().document_model
SignatoryModel = TransactionModel().signatory_model

@method_decorator(csrf_exempt, name='dispatch')
class TransactionWebhook(DetailView):
    model = TransactionModel
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_context_data(self, **kwargs):
        transaction = self.get_object()
        # do something

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({"done": "done"}, **response_kwargs)