from django.db import models
from django.template import engines
from django.template.loader import render_to_string

from mighty.fields import JSONField

template_engine = engines['django']


class Template(Base):
    template = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=256, null=True, blank=True)
    raw_template = models.TextField(null=True, blank=True)
    cfg_template = JSONField(blank=True, null=True)
    var_template = JSONField(blank=True, null=True)
    is_template = models.BooleanField(default=False)
    model_activate_template = True

    class Meta:
        abstract = True

    def compiled_template(self):
        template = django_engine.from_string(self.raw_template)
        return render_to_string(template, var_template)

    def context_form(self):
        return
