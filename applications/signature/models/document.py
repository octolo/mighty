from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from mighty.models.base import Base
from mighty.fields import JSONField
from mighty.applications.signature import choices as _c
from mighty.applications.signature.apps import SignatureConfig as conf

class TransactionDocument(Base):
    transaction = models.ForeignKey(conf.transaction_relation, on_delete=models.CASCADE, related_name="transaction_to_document")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    backend_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=_c.STATUS_DOCUMENT, default=_c.PREPARATION)
    to_sign = models.BooleanField(default=True)
    object_signed_id = models.PositiveIntegerField(blank=True, null=True)
    nb_signatories = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s(%s)" % (str(self.content_object), str(self.transaction))

    class Meta:
        abstract = True

    def pre_save(self):
        self.set_nb_signatories()


    def set_nb_signatories(self):
        self.nb_signatories = self.transaction.transaction_to_signatory.filter(role=_c.SIGNATORY).count()


    @property
    def is_document(self):
        return True if self.content_object.is_document else False
    @property
    def document(self):
        return self.content_object
    @property
    def locations(self):
        return self.signatory_to_location.all()

    def getattr_document(self, attr):
        if hasattr(self.document, attr):
            return getattr(self.document, attr)
        raise NotImplementedError("Document need attribute : %s" % attr)

    @property
    def document_name(self):
        return self.getattr_document("document_name")
    @property
    def name(self):
        return self.document_name
    @property
    def document_sign(self):
        return self.getattr_document("document_sign")
