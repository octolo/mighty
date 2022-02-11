from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class SignatureBackend:
    in_error = False
    backend = None
    transaction = None

    def transaction(self):
        raise NotImplementedError()

    def member(self):
        raise NotImplementedError()

    def document(self):
        raise NotImplementedError()

    @property
    def webhook_transaction_url(self):
        return reverse("octolo:wbg-signature-transaction", self.transaction.uid)
