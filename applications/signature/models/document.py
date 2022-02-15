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
    location = JSONField(blank=True, null=True)
    to_sign = models.BooleanField(default=True)
    object_signed_id = models.PositiveIntegerField()

    class Meta:
        abstract = True

    @property
    def is_document(self):
        return True if self.content_object.is_document else False

    @property
    def concept(self):
        return self.content_object.get_concept()

    def set_height(self, height):
        self.location["height"] = height
    def set_width(self, width):
        self.location["width"] = width
    def set_coordx(self, x):
        self.location["x"] = x
    def set_coordy(self, y):
        self.location["y"] = y

    def get_height(self):
        return self.location.get("height")
    def get_width(self):
        return self.location.get("width")
    def get_coordx(self):
        return self.location.get("x")
    def get_coordy(self):
        return self.location.get("y")

    @property
    def height(self):
        return self.get_height()
    @property
    def width(self):
        return self.get_width()
    @property
    def coordx(self):
        return self.get_coordx()
    @property
    def coordy(self):
        return self.get_coordy()
