from django.db import models
from django.utils.html import format_html

from mighty.models.base import Base
from mighty.models.image import Image
from mighty.applications.nationality import translates as _
from mighty.fields import JSONField

class Nationality(Base, Image):
    country = models.CharField(_.country, max_length=255)
    alpha2 = models.CharField(_.alpha2, max_length=2)
    alpha3 = models.CharField(_.alpha3, max_length=3, blank=True, null=True)
    numeric = models.CharField(_.numeric, max_length=3, blank=True, null=True)
    numbering = models.PositiveSmallIntegerField(_.numbering, blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_nationality
        verbose_name_plural = _.vp_nationality
        ordering = ['country', ]

    def __str__(self):
        return "%s (%s, %s, %s)" % (self.country, self.alpha2, self.alpha3, self.numeric)

    @property
    def image_html(self):
        if self.image:
            return format_html('<img src="%s" title="%s" style="max-height: 20px">' % (self.image.url, str(self)))
        return 

class Translator(Base):
    name = models.CharField(max_length=255)

    class Meta(Base.Meta):
        abstract = True

class TranslateDict(Base):
    language = models.ForeignKey('mighty.nationality', on_delete=models.CASCADE)
    translator = models.ForeignKey('mighty.translator', on_delete=models.CASCADE)
    precision = models.CharField(max_length=3)
    translates = JSONField()

    class Meta(Base.Meta):
        abstract = True