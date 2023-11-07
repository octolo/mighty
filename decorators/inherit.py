from django.utils.module_loading import import_string

def InheritClassList(inherit_list=()):
    def decorator(cls):
        inherit_classes = tuple(import_string(i) for i in inherit_list)
        InheritClasses = type("InheritClasses", inherit_classes, {})
        class NewClass(cls, InheritClasses): pass
        NewClass.__name__ = cls.__name__
        return NewClass
    return decorator


def InheritModelClassList(inherit_list=()):
    def decorator(cls):
        inherit_classes = tuple(import_string(i) for i in inherit_list)
        InheritClasses = type("InheritClasses", inherit_classes, {})
        class NewClass(cls, InheritClasses):
            class Meta(cls.Meta):
                abstract = True
        NewClass.__name__ = cls.__name__
        return NewClass
    return decorator
