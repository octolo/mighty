"""
Model class
Add search field at the model

(get_search) return the search field with searchable words
(set_search) set the search field with searchable words
"""
from django.db import models
from mighty.functions import make_searchable

class Search(models.Model):
    search = models.TextField(db_index=True, blank=True, null=True)

    class Meta:
        abstract = True

    def get_search(self):
        return make_searchable(str(self.__str__()))

    def set_search(self):
        self.search = self.get_search()

    def save(self, *args, **kwargs):
        self.set_search()
        super().save(*args, **kwargs)