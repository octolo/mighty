default_app_config = 'mighty.applications.logger.apps.LoggerConfig'

from django.utils.functional import cached_property
import logging

class EnableLogger:
    cache_logger = None

    def reload_logger(self):
        self.cache_logger = logging.getLogger(__name__)

    @property
    def logger(self):
        if not self.cache_logger:
            self.reload_logger()
        return self.cache_logger


    class locally:
        logs = []

        def reset(self):
            self.logs = []

        def warning(self, message, *args, **kwargs):
            self.logs.append((logging.WARNING, message, args, kwargs))

        def error(self, message, *args, **kwargs):
            self.logs.append((logging.ERROR, message, args, kwargs))

        def info(self, message, *args, **kwargs):
            self.logs.append((logging.INFO, message, args, kwargs))

        def debug(self, message, *args, **kwargs):
            self.logs.append((logging.DEBUG, message, args, kwargs))

    @cached_property
    def loglocally(self):
        return self.locally()

def format_log_field(field, value, instance, fk_column, fk_field):
    return {
        fk_column: instance,
        'field': field,
        'value': bytes(str(value), 'utf-8'),
        'fmodel': instance.fields()[field],
        'date_begin': instance._unmodified.date_update,
        'user': instance._unmodified.update_by,
    }

def EnableAccessLog(model, excludes=()):
    def deco(cls):
        setattr(cls, "accesslog_model", model)
        setattr(cls, "accesslog_exclude", excludes+(str(model.__name__).lower(),))
        return cls
    return deco

def createorupdate_changeslog(instance, newvalues, oldvalues, *args, **kwargs):
    fk_column = kwargs.get("fk_column", "object_id")
    fk_field = kwargs.get("fk_field", "id")
    if len(oldvalues) > 0:
        instance.changelog_model.objects.bulk_create([
            instance.changelog_model(
                **format_log_field(field, value, instance, fk_column, fk_field)
            ) for field, value in oldvalues.items()
        ])

