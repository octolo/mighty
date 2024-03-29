from django.db import  models
from mighty.models.base import Base
from mighty.models.keyword import Keyword
from mighty.fields import RichTextField

class News(Base, Keyword):
    keywords_fields = ['title',]
    title = models.CharField(max_length=255)
    news = RichTextField(blank=True, null=True)
    date_news = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_news',]

    def __str__(self):
        return "%s - %s" % (str(self.date_news), self.title)
