from django.contrib.contenttypes.models import ContentType

from mighty.applications.logger import EnableLogger


def check_status_task(ct, pk, task, task_id):
    model = ContentType.objects.get(id=ct).model_class()
    obj = model.objects.get(pk=pk)
    obj.task_status[task]['status'] = TASK_STATUS[1]
    obj.task_status[task]['task_id'] = task_id
    obj.save()


class TaskBackend(EnableLogger):
    def __init__(self, ct, pk, task, *args, **kwargs):
        self.ct = ct
        self.pk = pk
        self.task = task
        self.extra_args = args
        self.extra_kwargs = kwargs

    def start(self):
        raise NotImplementedError('Subclasses should implement start()')

    def cancel(self):
        raise NotImplementedError('Subclasses should implement cancel()')

    def end(self):
        raise NotImplementedError('Subclasses should implement end()')

    def error(self):
        raise NotImplementedError('Subclasses should implement error()')
