import logging

from celery import shared_task
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


@shared_task
def start_task(ct, pk, task, task_id, *args, **kwargs):
    model = ContentType.objects.get(id=ct).model_class()
    logger.info(f'start task {model}: {task} -> {task_id}')
    obj = model.objects.get(pk=pk)
    obj.task_last = task
    obj.task_status = 'RUNNING'
    obj.save()
    try:
        getattr(obj, f'task_{task.lower()}')(**kwargs)
    except Exception:
        obj.task_status = 'ERROR'
        obj.save()
        logger.warning(f'error task ({obj.task_status}) {model}: {task} -> {task_id}')
        raise
    obj.task_status = 'FINISH'
    obj.can_use_task = False
    obj.save()
    logger.info(f'end task ({obj.task_status}) {model}: {task} -> {task_id}')
