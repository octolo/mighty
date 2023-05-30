from mighty.backend import Backend
from mighty.applications.signature import choices as _c

class SignatureBackend(Backend):
    in_error = False
    backend = None
    transaction = None

    def __init__(self, path, transaction, *args, **kwargs):
        self.transaction = transaction
        self.transaction.backend = path.replace(".SignatureBackend", "")

    @property
    def _c(self):
        return _c

    @property
    def path(self):
        return self.transaction.backend


    # TRANSACTIONS
    def status_transaction(self):
        raise NotImplementedError("Subclasses should implement status_transaction()")

    def create_transaction(self):
        raise NotImplementedError("Subclasses should implement create_transaction()")

    def cancel_transaction(self):
        raise NotImplementedError("Subclasses should implement cancel_transaction()")

    def remind_transaction(self):
        raise NotImplementedError("Subclasses should implement remind_transaction()")

    def start_transaction(self):
        raise NotImplementedError("Subclasses should implement start_transaction()")

    def end_transaction(self):
        raise NotImplementedError("Subclasses should implement end_transaction()")

    # DOCUMENTS
    @property
    def documents(self):
        return self.transaction_to_document.all()

    def add_document(self, document):
        raise NotImplementedError("Subclasses should implement add_document()")

    def add_all_documents(self):
        raise NotImplementedError("Subclasses should implement add_all_documents()")

    def remove_document(self, document):
        raise NotImplementedError("Subclasses should implement remove_document()")

    def remove_all_documents(self, document):
        raise NotImplementedError("Subclasses should implement remove_all_documents()")


    # SIGNATORIES
    @property
    def signatories(self):
        return self.transaction_to_signatory.all()

    def add_signatory(self, signatory):
        raise NotImplementedError("Subclasses should implement add_signatory()")

    def add_all_signatories(self):
        raise NotImplementedError("Subclasses should implement add_all_signatories()")

    # LOCATIONS
    @property
    def locations(self):
        return self.transaction_to_location.all()

    def add_location(self, location):
        raise NotImplementedError("Subclasses should implement add_location()")

    def add_all_locations(self):
        raise NotImplementedError("Subclasses should implement add_all_locations()")
