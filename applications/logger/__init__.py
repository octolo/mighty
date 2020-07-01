default_app_config = 'mighty.applications.logger.apps.LoggerConfig'

def EnableChangeLog(model, excludes=()):
    def deco(cls):
        setattr(cls, "changelog_model", model)
        setattr(cls, "changelog_exclude", excludes+(str(model.__name__).lower(),))
        return cls
    return deco

def createorupdate_changeslog(instance, newvalues, oldvalues, *args, **kwargs):
    fk_column = kwargs.get("fk_column", "object_id")
    fk_field = kwargs.get("fk_field", "id")
    if len(oldvalues) > 0:
        instance.changelog_model.objects.bulk_create([
            instance.changelog_model(**{
                fk_column: instance,
                'field': field,
                'value': bytes(str(value), 'utf-8'),
                'fmodel': instance.fields()[field],
                'date_begin': instance._unmodified.date_update,
                'user': instance._unmodified.update_by,
            }) for field, value in oldvalues.items()
        ])