from mighty.fields import base

def EnableTimelineModel(model, excludes=()):
    def deco(cls):
        setattr(cls, "timeline_model", model)
        setattr(cls, "timeline_exclude", excludes+base+(str(model.__name__).lower(),))
        return cls
    return deco