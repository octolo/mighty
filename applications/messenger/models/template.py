
from django.db import models
from mighty.models.base import Base
from mighty.fields import RichTextField

class Template(Base):
    name = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    template = RichTextField(blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "template"
        verbose_name_plural = "templates"
