from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from mighty.decorators.tasked import TASK_STATUS
import logging
logger = logging.getLogger(__name__)

@shared_task
def start_task(ct, pk, task, task_id, *args, **kwargs):
    model = ContentType.objects.get(id=ct).model_class()
    logger.info("start task %s: %s -> %s" % (model, task, task_id))
    obj = model.objects.get(pk=pk)
    obj.task_status[task] = {"status": TASK_STATUS[0], "task_id": task_id}
    obj.save()
    try:
        getattr(obj, "task_%s"%task.lower())()
    except Exception as e:
        obj.task_status[task]["status"] = TASK_STATUS[2]
    obj.task_status[task]["status"] = TASK_STATUS[1]
    obj.save()
    log_msg = "end task (%s) %s: %s -> %s" % (obj.task_status[task]["status"], model, task, task_id)
    if obj.task_status[task]["status"] == TASK_STATUS[2]:
        logger.error(log_msg)
    else:
        logger.info(log_msg)