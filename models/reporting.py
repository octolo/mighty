from django.db import models
from django.contrib.contenttypes.models import ContentType

from mighty.models.base import Base
from mighty.functions import make_searchable
from mighty.fields import JSONField
from mighty.filegenerator import FileGenerator

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

    def __str__(self):
        return self.name

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
        return [f["title"] for f in self.config]

    @property
    def reporting_fields(self):
        return [f["data"] for f in self.config]

    def reporting_data_obj(self, field, obj):
        return getattr(obj, field)() if isinstance(getattr(type(obj), field), property) else getattr(obj, field)

    @property
    def reporting_items(self):
        return [(self.reporting_data_obj(field, obj) for field in self.reporting_fields) for obj in self.reporting_queryset]

    @property
    def reporting_file_generator(self):
        print("start")
        print("header", self.reporting_header)
        print("fields", self.reporting_fields)
        print("data", self.reporting_items)
        return FileGenerator(filename=self.file_name, items=self.reporting_items, fields=self.reporting_fields)

    def reporting_file_response(self, response, file_type):
        if response == "http":
            return self.reporting_file_generator.response_http(file_type)
        return self.reporting_file_generator.response_file(file_type)
