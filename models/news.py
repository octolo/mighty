from django.db import models

from mighty.fields import RichTextField
from mighty.models.base import Base
from mighty.models.keyword import Keyword


class News(Base, Keyword):
    keywords_fields = ['title']
    title = models.CharField(max_length=255)
    news = RichTextField(blank=True, null=True)
    date_news = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_news']

    def __str__(self):
        return f'{self.date_news!s} - {self.title}'
