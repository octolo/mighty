from django.db import models
from django.urls import reverse

from mighty.models.base import Base
from mighty.applications.signature import choices as _c, get_signature_backend

class Transaction(Base):
    name = models.CharField(max_length=255)
    backend = models.CharField(max_length=255)
    backend_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=_c.STATUS_TRANSACTION, default=_c.PREPARATION)

    class Meta:
        abstract = True

    @property
    def document_model(self):
        return self.transaction_to_document.model

    @property
    def signatory_model(self):
        return self.transaction_to_signatory.model

    @property
    def location_model(self):
        return self.transaction_to_location.model

    @property
    def documents(self):
        return self.transaction_to_document.all()

    @property
    def signatories(self):
        return self.transaction_to_signatory.all()

    @property
    def locations(self):
        return self.transaction_to_location.all()

    @property
    def webhook_url(self):
        return reverse("wbh-signature-transaction", self.transaction.uid)

    @property
    def signature_backend(self):
        backend, path = get_signature_backend(self.backend if self.backend else None)
        return backend(path=path, transaction=self)

    def create_transaction(self):
        self.signature_backend.create_transaction()

    def cancel_transaction(self):
        self.signature_backend.cancel_transaction()
    
    def remind_transaction(self):
        self.signature_backend.remind_transaction()