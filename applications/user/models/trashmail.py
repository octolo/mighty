from django.db import models

from mighty.models import Base


class Trashmail(Base):
    domain = models.CharField(max_length=255)

    class Meta(Base.Meta):
        abstract = True

    def __str__(self):
        return '@' + self.domain
