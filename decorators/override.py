from mighty import over_config


def OverrideClass(**kwargs):
    def decorator(obj):
        class OverrideCLS:
            pass

        over_config(OverrideCLS, kwargs.get('data', {}))

        class NewClass(obj, OverrideCLS):
            pass

        NewClass.__name__ = obj.__name__
        return NewClass

    return decorator
