from mighty.functions import models_difference, to_binary
from mighty.fields import base
from mighty.applications.logger import createorupdate_changeslog
from channels.db import database_sync_to_async

def pre_change_log(sender, instance, **kwargs):
    try:
        instance._unmodified = type(instance).objects.get(pk=instance.pk)
    except type(instance).DoesNotExist:
        instance._pre_save_instance = instance

def post_change_log(sender, instance, created, **kwargs):
    if not created:
        new, old = models_difference(instance, instance._unmodified, base+instance.changelog_exclude)
        createorupdate_changeslog(instance, new, old)