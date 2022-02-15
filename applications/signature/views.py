from mighty.views import ModelViewSet
from mighty.applications.signature import get_transaction_model
from mighty.applications.signature.serializers import (
    TransactionSerializer, TransactionDocumentSerializer, TransactionSignatorySerializer)

TransactionModel = get_transaction_model()
DocumentModel = TransactionModel().document_model
SignatoryModel = TransactionModel().signatory_model

class TransactionApiViewSet(ModelViewSet):
    queryset = TransactionModel.objects.all()
    serializer_class = TransactionSerializer

class TransactionDocumentApiViewSet(ModelViewSet):
    queryset = SignatoryModel.objects.all()
    serializer_class = TransactionDocumentSerializer

class TransactionSignatoryApiViewSet(ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = TransactionSignatorySerializer