from mighty.forms.descriptors import ModelFormDescriptable

class TaskForm(ModelFormDescriptable):
    class Meta:
        fields = ("task_list",)
