from rest_framework.response import Response
from rest_framework.decorators import action

from mighty.filters import ParamFilter
from mighty.views import ModelViewSet
from mighty.applications.signature import get_transaction_model
from mighty.applications.signature.serializers import (
    TransactionSerializer, TransactionDocumentSerializer, TransactionSignatorySerializer)

TransactionModel = get_transaction_model()
DocumentModel = TransactionModel().document_model
SignatoryModel = TransactionModel().signatory_model

generic_filters = [
    ParamFilter(id="transaction", field="transaction__uid")
]

class TransactionApiViewSet(ModelViewSet):
    queryset = TransactionModel.objects.all()
    serializer_class = TransactionSerializer

class TransactionDocumentApiViewSet(ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = TransactionDocumentSerializer
    pagination_class = None
    filters = generic_filters

class TransactionSignatoryApiViewSet(ModelViewSet):
    queryset = SignatoryModel.objects.all()
    serializer_class = TransactionSignatorySerializer
    pagination_class = None
    filters = generic_filters

    @action(detail=True, methods=['post'])
    def add_or_update_location(self, request, uid, pk=None):
        signatory = self.get_object()
        signatory.set_all_attr(**request.data)
        signatory.save()
        serializer = self.get_serializer(signatory)
        return Response(serializer.data)
