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
    class Meta:
        model = TransactionModel
        fields = ("uid",) + fields.transaction

class TransactionDocumentSerializer(ModelSerializer):
    transaction = SlugRelatedField(slug_field="uid", queryset=TransactionModel.objects.all())

    class Meta:
        model = DocumentModel
        fields = ("uid",) + fields.document

class TransactionSignatorySerializer(ModelSerializer):
    transaction = SlugRelatedField(slug_field="uid", queryset=TransactionModel.objects.all())
    signatory = SlugRelatedField(slug_field="uid", queryset=SignatoryFollow.objects.all(), required=False)

    class Meta:
        model = SignatoryModel
        fields = ("uid",) + fields.signatory

class TransactionLocationSerializer(ModelSerializer):
    transaction = SlugRelatedField(slug_field="uid", queryset=TransactionModel.objects.all())
    signatory = SlugRelatedField(slug_field="uid", queryset=SignatoryModel.objects.all())
    document = SlugRelatedField(slug_field="uid", queryset=DocumentModel.objects.all())

    class Meta:
        model = LocationModel
        fields = ("uid",) + fields.location
