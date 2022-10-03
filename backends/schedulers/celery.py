from celery import shared_task
from django.contrib.contenttypes.models import ContentType
import logging
logger = logging.getLogger(__name__)

@shared_task
def start_task(ct, pk, task):
    model = ContentType.objects.get(id=ct).model_class()
    logger.info("start task %s: %s" % (model, task))
    obj = model.objects.get(pk=pk)
    obj.task_status[task] = True
    obj.save()
    getattr(obj, "task_%s"%task.lower())()
    obj.task_status[task] = False
    obj.save()