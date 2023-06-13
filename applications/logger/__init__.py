default_app_config = 'mighty.applications.logger.apps.LoggerConfig'

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


def format_log_field(field, value, instance, fk_column, fk_field):
    return {
        fk_column: instance,
        'field': field,
        'value': bytes(str(value), 'utf-8'),
        'fmodel': instance.fields()[field],
        'date_begin': instance._unmodified.date_update,
        'user': instance._unmodified.update_by,
    }

#def ModelChangelog(model, on_delete=None):
#    from mighty.applications.logger.models import ChangeLog
#    from django.db import models
#    model_name = model.split(".")[-1]
#    ChangeLog.__name__ = model_name+"ChangeLog"
#    class NewChangeLog(ChangeLog):
#        object_id = models.ForeignKey(model, on_delete=models.CASCADE, related_name=model_name.lower()+"change_log")
#        class Meta:
#            label = model.split(".")[0l]
#    return NewChangeLog

def EnableChangeLog(model, excludes=()):
    def deco(cls):
        setattr(cls, "changelog_model", model)
        setattr(cls, "changelog_exclude", excludes+(str(model.__name__).lower(),))
        return cls
    return deco

#def EnableChangeLogV2(**kwargs):
#    from django.db import models
#    import types
#    def decorator(obj):
#        from mighty.applications.logger.models import ChangeLog
#        class ChangeLog(ChangeLog):
#            object_id = models.ForeignKey(kwargs["fk"], on_delete=models.CASCADE)
#
#            clas
#        #setattr(cls, "changelog_model", LogModel)
#        #setattr(cls, "changelog_exclude", kwargs.get("excludes", ())+(str(LogModel.__name__).lower(),))
#        return obj#, LogModel
#    return decorator#, LogModel

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

