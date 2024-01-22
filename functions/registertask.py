
def subscribe_register_task(named_id, obj, id=None, **kwargs):
    from mighty.models import RegisterTaskSubscription
    from django.contrib.contenttypes.models import ContentType
    return RegisterTaskSubscription.objects.get_or_create(
        register__named_id=named_id,
        content_type_subscriber=ContentType.objects.get_for_model(obj),
        object_id_subscriber=obj.pk,
        object_id=id,
    )

def unsubscribe_register_task(named_id, obj, id=None, **kwargs):
    from mighty.models import RegisterTaskSubscription
    from django.contrib.contenttypes.models import ContentType
    rts = RegisterTaskSubscription.objects.get(
        register__named_id=named_id,
        register__content_type=ContentType.objects.get_for_model(obj),
        content_type_subscriber=ContentType.objects.get_for_model(obj),
        object_id_subscriber=obj.pk,
        object_id=id,
    )
    if rts:
        rts.delete()
