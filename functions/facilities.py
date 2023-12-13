from functools import reduce

def getattr_recursive(obj, strtoget, split="."):
    return reduce(getattr, [obj, ]+strtoget.split(split)) if strtoget else strtoget
