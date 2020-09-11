"""
Model class
Add [sources] JSON field at the model

[sources_configuration] configurtion sources
(field_configuration) get the configuration source of the field
(add_source) add a source to a field
(delete_source) delete a source to a field
(add_extend_source) add an extended source to a field
(delete_extend_source) delete an extended source to a field
(clean_sources) clean souces with the configuration sources
"""
from django.db import models
from mighty.models import JSONField
from mighty.models.base import Base
from mighty.models.file import File
from mighty import translates as _

TYPE_WEBSITE = 'WEBSITE'
TYPE_DOCUMENT = 'DOCUMENT'
TYPE_IMAGE = 'IMAGE'
TYPE_FLUX = 'FLUX'
TYPE_EVENT = 'EVENT'
TYPE_OTHER = 'OTHER'
CHOICES_TYPE = (
    (TYPE_WEBSITE, _.TYPE_WEBSITE),
    (TYPE_DOCUMENT, _.TYPE_DOCUMENT),
    (TYPE_IMAGE, _.TYPE_IMAGE),
    (TYPE_FLUX, _.TYPE_FLUX),
    (TYPE_EVENT, _.TYPE_EVENT),
    (TYPE_OTHER, _.TYPE_OTHER),)
CHOICES_TYPE = sorted(list(CHOICES_TYPE), key=lambda x: x[1])
class SourceModel(Base, File):
    sourcetype = models.CharField(max_length=10, choices=CHOICES_TYPE, default=TYPE_OTHER)
    object_id = models.ForeignKey('', on_delete=models.CASCADE)
    field = models.CharField(_.field, max_length=255, db_index=True)
    desc = JSONField(blank=True, null=True)
    date_begin = models.DateField(_.date_begin)
    date_end = models.DateField(_.date_end, null=True, blank=True)
    user = models.CharField(max_length=255)

    class Meta:
        abstract = True
        verbose_name = _.v_source
        verbose_name_plural = _.vp_source
        ordering = ['-date_begin']

    @property
    def get_value(self):
        return self.value.decode('utf-8')

#from django.db import models
#from mighty.models import JSONField
#from mighty.translates import choices as _
#from mighty.functions import test
#
#TYPE_SITE = 'TYPE_SITE'
#TYPE_DOCUMENT = 'TYPE_DOCUMENT'
#TYPE_OTHER = 'TYPE_OTHER'
#TYPE_NONE = 'TYPE_NONE'
#CHOICES_TYPE = (
#    (TYPE_SITE, _.TYPE_SITE),
#    (TYPE_DOCUMENT, _.TYPE_DOCUMENT),
#    (TYPE_OTHER, _.TYPE_OTHER),
#    (TYPE_NONE, _.TYPE_NONE))
#class Source(models.Model):
#    sources_configuration = {}
#    sources = JSONField(blank=True, null=True)
#
#    class Meta:
#        abstract = True
#
#    def field_configuration(self, field):
#        return self.sources_configuration[field]
#
#    def add_extend_source(self, field, key, value):
#        if self.sources is not None and field in self.sources:
#            self.sources[field][key] = value
#
#    def delete_extend_source(self, field, key):
#        if self.sources is not None and field in self.sources and key in self.sources[field]:
#            del self.sources[field][key]
#
#    def add_source(self, field, source):
#        if test(getattr(self, field)):
#            if self.sources is None: self.sources = {}
#            self.sources[field] = source
#        elif self.sources is not None and field in self.sources:
#            self.delete_source(field)
#            if not self.sources: self.sources = None
#
#    def delete_source(self, field):
#        if field in self.sources:
#            del self.sources[field]
#        if not self.sources: self.sources = None
#
#    def clean_sources(self):
#        for field in self.fields():
#            if field in self.sources_configuration:
#                self.add_source(field, self.field_configuration(field))
#
#    def save(self, *args, **kwargs):
#        self.clean_sources()
#        super().save(*args, **kwargs)