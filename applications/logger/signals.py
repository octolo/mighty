from mighty.functions import models_difference, to_binary
from mighty.fields import base

def pre_change_log(sender, instance, **kwargs):
    try:
        instance._unmodified = type(instance).objects.get(pk=instance.pk)
    except type(instance).DoesNotExist:
        instance._pre_save_instance = instance

def post_change_log(sender, instance, created, **kwargs):
    if not created:
        new, old = models_difference(instance, instance._unmodified, base+instance.changelog_exclude)
        instance.changelog_model.objects.bulk_create([
            instance.changelog_model(**{
                'model_id': instance,
                'field': field,
                'value': bytes(value, 'utf-8'),
                'fmodel': instance.fields()[field],
                'date_begin': instance._unmodified.date_update,
                'user': instance._unmodified.update_by,
            }) for field, value in old.items()
        ])