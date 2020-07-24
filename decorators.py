from mighty.fields import base
from django.db import models

def EnableTimelineModel(model, excludes=()):
    def deco(cls):
        setattr(cls, "timeline_model", model)
        setattr(cls, "timeline_exclude", excludes+base+(str(model.__name__).lower(),))
        return cls
    return deco

def EnableSourceModel(model, excludes=()):
    def deco(cls):
        setattr(cls, "source_model", model)
        setattr(cls, "source_exclude", excludes+base+(str(model.__name__).lower(),))
        return cls
    return deco