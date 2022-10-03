from django.db import models
from django.utils.module_loading import import_string
from mighty.fields import JSONField
from mighty.apps import MightyConfig

def TaskedModel(**kwargs):
    def decorator(obj):
        class TaskedModel(obj):
            task_list = models.CharField(max_length=25, blank=True, null=True, choices=kwargs.get("task_list", ()))
            task_status = JSONField(blank=True, null=True, default=dict)

            class Meta(obj.Meta):
                abstract = True

            def save(self, *args, **kwargs):
                if self.task_list:
                    self.start_task(self.task_list)
                self.task_list = None
                super().save(*args, **kwargs)

            def backend_task(self, task):
                return import_string("%s.TaskBackend" % MightyConfig.backend_task)(
                    ct=self.get_content_type().id,
                    pk=self.pk,
                    task=task)
                
            def task_is_running(self, task):
                return (task in self.task_status and self.task_status[task])

            def start_task(self, task):
                if not self.task_is_running(task):
                    self.backend_task(task).start()
        return TaskedModel
    return decorator