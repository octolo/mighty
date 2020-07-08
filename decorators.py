from mighty.fields import base

def EnableHistoryModel(model, excludes=()):
    def deco(cls):
        setattr(cls, "history_model", model)
        setattr(cls, "history_exclude", excludes+base+(str(model.__name__).lower(),))
        return cls
    return deco

def EnableSourceModel(model, excludes=()):
    def deco(cls):
        setattr(cls, "source_model", model)
        setattr(cls, "source_exclude", excludes+base+(str(model.__name__).lower(),))
        return cls
    return deco