from django.db import models
from django.utils.module_loading import import_string
from mighty.fields import JSONField
from mighty.apps import MightyConfig

TASK_STATUS = (
    ("AVAILABLE", "AVAILABLE"),
    ("RUNNING", "RUNNING"),
    ("FINISH", "FINISH"),
    ("ERROR", "ERROR"),
)

def TaskedModel(**kwargs):
    def decorator(obj):
        class TaskedModel(obj):
            task_list = models.CharField(max_length=252, blank=True, null=True, choices=kwargs.get("task_list", ()))
            task_status = models.CharField(max_length=25, choices=TASK_STATUS, default="AVAILABLE")
            task_last = models.CharField(max_length=252, blank=True, null=True)
            can_use_task = True

            class Meta(obj.Meta):
                abstract = True

            def task_save(self, *args, **kwargs):
                if self.task_list:
                    self.start_task(self.task_list)
                self.task_list = None

            def backend_task(self, task, *args, **kwargs):
                self._logger.warning("backend_task %s" % task)
                self._logger.warning("ct %s" % self.get_content_type().id)
                self._logger.warning("pk %s" % self.pk)
                return import_string("%s.TaskBackend" % MightyConfig.backend_task)(
                    ct=self.get_content_type().id,
                    pk=self.pk,
                    task=task,
                    *args, **kwargs)

            def task_is_running(self, task):
                return (self.task_status == "RUNNING" and self.task_last == task)

            def start_task(self, task, *args, **kwargs):
                if not self.task_is_running(task) and self.can_use_task:
                    self.backend_task(task, *args, **kwargs).start()

            @property
            def form_task(self):
                from mighty.forms import TaskForm
                class TaskForm(TaskForm):
                    class Meta:
                        model = type(self)
                        fields = ("task_list",)
                return TaskForm()

            @property
            def admin_task_url(self): return self.get_url('task', self.app_admin, arguments=self.admin_url_args)

        return TaskedModel
    return decorator
