
def subscribe_register_task(named_id, obj, id=None, **kwargs):
    from django.contrib.contenttypes.models import ContentType

    from mighty.models import RegisterTask, RegisterTaskSubscription
    rgs = RegisterTask.objects.get(named_id=named_id)
    return RegisterTaskSubscription.objects.get_or_create(
        register=rgs,
        content_type_subscriber=ContentType.objects.get_for_model(obj),
        object_id_subscriber=obj.pk,
        object_id=id,
    )


def unsubscribe_register_task(named_id, obj, id=None, **kwargs):
    from django.contrib.contenttypes.models import ContentType

    from mighty.models import RegisterTask, RegisterTaskSubscription
    rgs = RegisterTask.objects.get(named_id=named_id)
    rts = RegisterTaskSubscription.objects.get(
        register=rgs,
        content_type_subscriber=ContentType.objects.get_for_model(obj),
        object_id_subscriber=obj.pk,
        object_id=id,
    )
    if rts:
        rts.delete()
