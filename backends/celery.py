from mighty.backends import TaskBackend
from mighty.backends.schedulers.celery import start_task

class TaskBackend(TaskBackend):
    def start(self):
        start_task.delay(self.ct, self.pk, self.task)
