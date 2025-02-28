from mighty.fields import base


def EnableSourceModel(model, excludes=()):
    def deco(cls):
        cls.source_model = model
        cls.source_exclude = excludes + base + (str(model.__name__).lower(),)
        return cls

    return deco
