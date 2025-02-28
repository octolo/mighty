import logging

from celery import shared_task
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


@shared_task
def start_task(ct, pk, task, task_id, *args, **kwargs):
    model = ContentType.objects.get(id=ct).model_class()
    logger.info('start task %s: %s -> %s' % (model, task, task_id))
    obj = model.objects.get(pk=pk)
    obj.task_last = task
    obj.task_status = 'RUNNING'
    obj.save()
    try:
        getattr(obj, 'task_%s' % task.lower())(**kwargs)
    except Exception as e:
        obj.task_status = 'ERROR'
        obj.save()
        logger.warning('error task (%s) %s: %s -> %s' % (obj.task_status, model, task, task_id))
        raise e
    obj.task_status = 'FINISH'
    obj.can_use_task = False
    obj.save()
    logger.info('end task (%s) %s: %s -> %s' % (obj.task_status, model, task, task_id))
