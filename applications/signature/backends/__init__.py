import logging

logger = logging.getLogger(__name__)

class SignatureBackend:
    in_error = False
    transaction = None
    entity = None
    backend = None

    def create_transaction(self):
        raise NotImplementedError()

    def create_entity(self):
        raise NotImplementedError()