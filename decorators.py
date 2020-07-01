from mighty.fields import base

def EnableAnticipateModel(model, excludes=()):
    def deco(cls):
        setattr(cls, "anticipate_model", model)
        setattr(cls, "anticipate_exclude", excludes+base+(str(model.__name__).lower(),))
        return cls
    return deco

def EnableSourceModel(model, excludes=()):
    def deco(cls):
        setattr(cls, "source_model", model)
        setattr(cls, "source_exclude", excludes+base+(str(model.__name__).lower(),))
        return cls
    return deco