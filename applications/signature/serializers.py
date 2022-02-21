from django.conf import settings
from rest_framework.serializers import ModelSerializer, SlugRelatedField, SerializerMethodField
from mighty.applications.signature import get_transaction_model, fields
from mighty.applications.signature.apps import SignatureConfig as conf

TransactionModel = get_transaction_model()
DocumentModel = TransactionModel().document_model
LocationModel = TransactionModel().location_model
SignatoryModel = TransactionModel().signatory_model
SignatoryFollow = SignatoryModel().follow_model


class TransactionSerializer(ModelSerializer):
    documents = SlugRelatedField(slug_field='uid', many=True, queryset=DocumentModel.objects.all(), 
        allow_null=True, required=False, source="transaction_to_document")
    signatories = SlugRelatedField(slug_field='uid', many=True, queryset=SignatoryModel.objects.all(), 
        allow_null=True, required=False, source="transaction_to_signatory")

    class Meta:
        model = TransactionModel
        fields = fields.transaction_sz + ("documents", "signatories")

class TransactionDocumentSerializer(ModelSerializer):
    transaction = SlugRelatedField(slug_field="uid", queryset=TransactionModel.objects.all())

    class Meta:
        model = DocumentModel
        fields = fields.document_sz

class TransactionSignatorySerializer(ModelSerializer):
    transaction = SlugRelatedField(slug_field="uid", queryset=TransactionModel.objects.all(), required=False)
    signatory = SlugRelatedField(slug_field="uid", queryset=SignatoryFollow.objects.all(), required=False)

    class Meta:
        model = SignatoryModel
        fields = ("uid",) + fields.signatory_sz

class TransactionLocationSerializer(ModelSerializer):
    transaction = SlugRelatedField(slug_field="uid", queryset=TransactionModel.objects.all())
    signatory = SlugRelatedField(slug_field="uid", queryset=SignatoryModel.objects.all())
    document = SlugRelatedField(slug_field="uid", queryset=DocumentModel.objects.all())

    class Meta:
        model = LocationModel
        fields = fields.location_sz
