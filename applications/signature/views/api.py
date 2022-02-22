from rest_framework.response import Response
from rest_framework.decorators import action

from mighty.filters import ParamFilter
from mighty.views import ModelViewSet
from mighty.applications.signature import get_transaction_model
from mighty.applications.signature.serializers import (
    TransactionSerializer, TransactionDocumentSerializer, TransactionSignatorySerializer, TransactionLocationSerializer)

TransactionModel = get_transaction_model()
DocumentModel = TransactionModel().document_model
LocationModel = TransactionModel().location_model
SignatoryModel = TransactionModel().signatory_model

generic_filters = [
    ParamFilter(id="transaction", field="transaction__uid")
]

signatory_filters = [
    ParamFilter(id="signatory", field="signatory__uid"),
    ParamFilter(id="transaction", field="transaction__uid"),
    ParamFilter(id="document", field="document__uid")
]

class TransactionApiViewSet(ModelViewSet):
    queryset = TransactionModel.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=True, methods=["get"])
    def launch(self, request, uid, group_named_id, pk=None):
        transaction = self.get_object()
        documents = transaction.transaction_to_document.all()
        signatories = transaction.transaction_to_signatory.all()
        locations = transaction.transaction_to_location.all()
        launch_data = {
            'transaction': transaction,
            'documents': documents,
            'signatories': signatories,
            'locations': locations,
        }
        data = transaction.backend.launch_transaction(launch_data)
        # signature_backend.create_webhook()
        return Response(data)

class TransactionDocumentApiViewSet(ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = TransactionDocumentSerializer
    pagination_class = None
    filters = generic_filters

class TransactionLocationApiViewSet(ModelViewSet):
    queryset = LocationModel.objects.all()
    serializer_class = TransactionLocationSerializer
    pagination_class = None
    filters = signatory_filters

class TransactionSignatoryApiViewSet(ModelViewSet):
    queryset = SignatoryModel.objects.all()
    serializer_class = TransactionSignatorySerializer
    pagination_class = None
    filters = generic_filters
