from django.db import models
from django.contrib.contenttypes.models import ContentType

from mighty.models.base import Base
from mighty.functions import make_searchable
from mighty.fields import JSONField

class Backend(Base):
    service = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    backend = models.CharField(max_length=255, blank=True, null=True)
    backend_list = JSONField(default=list, blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ('service', 'content_type')

    def pre_save(self):
        if not self.service and self.content_type:
            self.service = str(self.content_type.app_label)+"."+str(self.content_type.model)

    @property
    def format_list(self):
        return [self.backend] if self.backend else self.backend_list
