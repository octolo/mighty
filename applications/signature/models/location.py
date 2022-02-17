from django.db import models
from mighty.models.base import Base
from mighty.applications.signature.apps import SignatureConfig as conf


class TransactionLocation(Base):
    transaction = models.ForeignKey(conf.transaction_relation, on_delete=models.CASCADE, related_name="transaction_to_signatory")
    signatory = models.ForeignKey(conf.signatory_relation, 
        on_delete=models.SET_NULL, blank=True, null=True, related_name="signatory_to_location"))
    document = models.ForeignKey(conf.document_relation, on_delete=models.CASCADE, related_name="document_to_location")
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

    def __str__(self):
        return "%s(%s)" % (str(self.signatory), str(self.transaction))

    class Meta:
        abstract = True
