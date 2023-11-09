from django.utils.module_loading import import_string

class InheritClass: pass

def InheritClassList(*args):
    def decorator(cls):
        inherit_classes = tuple(import_string(i) for i in args)
        class NewClass(cls, type("InheritClass", inherit_classes, {})): pass
        NewClass.__name__ = cls.__name__
        return NewClass
    return decorator

def InheritModelClassList(*args, **kwargs):
    def decorator(cls):
        inherit_classes = tuple(import_string(i) for i in args)
        class NewClass(cls, type("InheritClass", inherit_classes, {})):
            class Meta(cls.Meta):
                abstract = kwargs.get("abstract", True)
        NewClass.__name__ = cls.__name__
        return NewClass
    return decorator
