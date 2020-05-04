"""
Model class
Add an [uid] at the model and generate urls based on

(detail_url) return the detail url
(change_url) return the change url
(delete_url) return the delete url
"""
from django.db import models
from django.urls import reverse
from uuid import uuid4

class Uid(models.Model):
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)

    class Meta:
        abstract = True

    @property
    def detail_url(self): return self.get_url('detail', arguments={"uid": self.uid})
    @property
    def change_url(self): return self.get_url('change', arguments={"uid": self.uid})
    @property
    def delete_url(self): return self.get_url('delete', arguments={"uid": self.uid})