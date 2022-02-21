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
