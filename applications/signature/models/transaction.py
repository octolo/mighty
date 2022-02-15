from django.db import models
from mighty.models.base import Base
from mighty.applications.signature import choices as _c

class Transaction(Base):
    name = models.CharField(max_length=255)
    backend = models.CharField(max_length=255)
    backend_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=_c.STATUS_TRANSACTION, default=_c.PREPARATION)

    class Meta:
        abstract = True

    @property
    def document_model(self):
        return type(self.transaction_to_document.model())

    @property
    def signatory_model(self):
        return type(self.transaction_to_signatory.model())
