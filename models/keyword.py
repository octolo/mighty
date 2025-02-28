"""
Model class
Add keywords field at the model to help searching ability
usefull for some text field search based.

[keywords_fields] list of fields to search for keywords
(get_keywords) return the keywords field searchable
(set_keywords) set the keywords field
"""

from django.db import models

from mighty.functions import weight_words


class Keyword(models.Model):
    keywords_fields = []
    keywords = models.CharField(max_length=255, blank=True, null=True)
    model_activate_keyword = True

    class Meta:
        abstract = True

    def get_keywords(self):
        words = []
        for field in self.keywords_fields:
            words += weight_words(getattr(self, field))
        return '_' + '_'.join(words)

    def set_keywords(self):
        self.keywords = self.get_keywords()
        if self.keywords:
            self.keyworkd = '_' + self.keywords

    def save(self, *args, **kwargs):
        self.set_keywords()
        super().save(*args, **kwargs)
