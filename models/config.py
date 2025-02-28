from django.db import models

from mighty.functions import make_searchable
from mighty.models.base import Base


class Config(Base):
    name = models.CharField(max_length=255, unique=True)
    url_name = models.CharField(max_length=255, null=True, blank=True, editable=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ('date_create', 'name')

    def save(self, *args, **kwargs):
        self.url_name = get_valid_filename(make_searchable(self.name))
        super().save(*args, **kwargs)
