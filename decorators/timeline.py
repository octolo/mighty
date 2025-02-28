from mighty.fields import base


def EnableTimelineModel(model, excludes=()):
    def deco(cls):
        cls.timeline_model = model
        cls.timeline_exclude = excludes + base + (str(model.__name__).lower(),)
        return cls
    return deco
