from django.db import models
from django.urls import reverse

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

    @property
    def webhook_url(self):
        return reverse("wbh-signature-transaction", self.transaction.uid)

    #def start_transaction(self):
    #    backend = get_backend()
    #    backend = backend(transaction=self)
    #    backend.start_transaction()
