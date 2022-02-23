from django.db import models
from mighty.models.base import Base
from mighty.applications.signature.apps import SignatureConfig as conf

class TransactionLocationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(disable=False)

class TransactionLocation(Base):
    transaction = models.ForeignKey(conf.transaction_relation, on_delete=models.CASCADE, related_name="transaction_to_location")
    signatory = models.ForeignKey(conf.location_relation,
        on_delete=models.CASCADE, related_name="signatory_to_location")
    document = models.ForeignKey(conf.document_relation, on_delete=models.CASCADE, related_name="document_to_location")
    backend_id = models.CharField(max_length=255, blank=True, null=True)
    height = models.PositiveIntegerField(default=80)
    width = models.PositiveIntegerField(default=120)
    x = models.PositiveIntegerField(default=0)
    y = models.PositiveIntegerField(default=0)
    yb = models.PositiveIntegerField(default=0)
    page = models.PositiveIntegerField()
    disable = models.BooleanField(default=False)

    objects = models.Manager()
    objectsB = TransactionLocationManager()

    def __str__(self):
        return "%s(%s)" % (str(self.signatory), str(self.transaction))

    class Meta:
        abstract = True

    def post_save(self):
        self.document.save()

    def post_delete(self):
        self._old_self.document.save()

    @property
    def color(self):
        return self.signatory.color

    @property
    def fullname(self):
        return self.signatory.fullname

    def add_to_transaction(self):
        self.transaction.signature_backend.add_location(self)