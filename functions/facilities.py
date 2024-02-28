from functools import reduce

def getattr_recursive(obj, strtoget, split=".", default=None):
    try:
        return reduce(getattr, [obj, ]+strtoget.split(split)) if strtoget else strtoget
    except AttributeError:
        return default
