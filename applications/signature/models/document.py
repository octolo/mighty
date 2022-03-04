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
    object_signed_id = models.PositiveIntegerField(blank=True, null=True)
    nb_signatories = models.PositiveIntegerField(default=0)
    nb_locations = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s(%s)" % (str(self.content_object), str(self.transaction))

    class Meta:
        abstract = True

    def pre_save(self):
        self.set_nb_signatories()
        self.set_nb_locations()

    def post_save(self):
        self.transaction.save()

    def set_nb_signatories(self):
        self.nb_signatories = self.document_to_location.distinct('signatory').count()

    def set_nb_locations(self):
        self.nb_locations = self.document_to_location.count()

    @property
    def object_uid(self):
        return self.document.uid if hasattr(self.document, "uid") else None
    @property
    def is_document(self):
        return True if self.content_object.is_document else False
    @property
    def document(self):
        return self.content_object
    @property
    def file_to_use(self):
        return self.getattr_document("file_to_use")
    @property
    def locations(self):
        return self.document_to_location.all()
    @property
    def to_sign(self):
        return self.locations.count() > 0

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

    def add_to_transaction(self):
        self.transaction.signature_backend.add_document(self)
