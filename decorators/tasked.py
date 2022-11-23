from django.db import models
from django.utils.module_loading import import_string
from mighty.fields import JSONField
from mighty.apps import MightyConfig

TASK_STATUS = ["running", "finish", "error"]

def TaskedModel(**kwargs):
    def decorator(obj):
        class TaskedModel(obj):
            task_list = models.CharField(max_length=252, blank=True, null=True, choices=kwargs.get("task_list", ()))
            task_status = JSONField(blank=True, null=True, default=dict)
            can_use_task = True

            class Meta(obj.Meta):
                abstract = True

            def save(self, *args, **kwargs):
                if self.task_list:
                    self.start_task(self.task_list)
                self.task_list = None
                super().save(*args, **kwargs)

            def backend_task(self, task, *args, **kwargs):
                return import_string("%s.TaskBackend" % MightyConfig.backend_task)(
                    ct=self.get_content_type().id,
                    pk=self.pk,
                    task=task,
                    *args, **kwargs)
                
            def task_is_running(self, task):
                return (task in self.task_status and 
                        "status" in self.task_status[task] and
                        self.task_status[task]["status"] == TASK_STATUS[0])

            def start_task(self, task, *args, **kwargs):
                if not self.task_is_running(task):
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
