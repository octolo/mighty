from django.db import models
from django.contrib.contenttypes.models import ContentType

from mighty.models.base import Base
from mighty.functions import make_searchable
from mighty.fields import JSONField

class Reporting(Base):
    name = models.CharField(max_length=255)
    file_name = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True, related_name="ct_to_reporting")
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True, related_name="ct_to_target")
    manager = models.CharField(max_length=255, default="objects")
    config = JSONField(default=list, blank=True, null=True)
    filter_config = JSONField(default=dict, blank=True, null=True)
    filter_related = JSONField(default=dict, blank=True, null=True)
    related_obj = None

    class Meta(Base.Meta):
        abstract = True
        ordering = ('name', 'content_type', 'target')

    @property
    def reporting_filter(self):
        Qfilter = {}
        if self.filter_config: 
            Qfilter.update(self.filter_config)
        if self.filter_config: 
            Qfilter.update({k: self.reporting_data_obj(self.related_obj, v) for k,v in self.filter_related.items()})
        return Qfilter

    @property
    def reporting_queryset(self):
        return getattr(self.target.model_class(), self.manager).filter(**self.reporting_filter)

    @property
    def reporting_header(self):
        return (field.title for field in self.file_config)

    @property
    def reporting_fields(self):
        return (field.data for field in self.file_config)
    
    def reporting_data_obj(self, field, obj):
        return getattr(obj, field)() if callable(obj, field) else getattr(obj, field)

    def reporting_items(self, objs):
        return [(self.reporting_data_obj(field, obj) for field in self.reporting_fields) for obj in self.reporting_queryset]

