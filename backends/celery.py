from mighty.backends import TaskBackend
from mighty.backends.schedulers.celery import start_task
from celery import uuid

class TaskBackend(TaskBackend):
    def start(self):
        task_id = uuid()
        start_task.apply_async(
            (self.ct, self.pk, self.task, task_id)+self.extra_args,
            self.extra_kwargs,
            task_id=task_id)