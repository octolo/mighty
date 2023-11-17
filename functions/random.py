from random import randrange
from datetime import timedelta

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def random_object_by_id(model, manager="objects", **kwargs):
    manager = getattr(model, manager)
    rand_object = randrange(0, manager.filter(**kwargs).count()-1)
    manager.get(pk=rand_object)

