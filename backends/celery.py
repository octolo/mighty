import logging

from celery import uuid

from mighty.backends import TaskBackend
from mighty.backends.schedulers.celery import start_task

logger = logging.getLogger(__name__)


class TaskBackend(TaskBackend):
    def start(self):
        task_id = uuid()
        args = (self.ct, self.pk, self.task, task_id) + self.extra_args
        start_task.apply_async(args, self.extra_kwargs, task_id=task_id)
