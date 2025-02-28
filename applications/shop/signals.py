from django.db.models.signals import m2m_changed

from mighty.models import Bill


def AddOrRemoveDiscount(sender, instance, action, **kwargs):
    if action in {'post_add', 'post_remove'}:
        instance.save()


m2m_changed.connect(AddOrRemoveDiscount, sender=Bill.discount.through)
