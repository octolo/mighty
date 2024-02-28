from django.db import  models
from django.contrib.contenttypes.models import ContentType
from django.template import Context, Template
from mighty.fields import RichTextField
from mighty.models.base import Base

class TemplateVariable(Base):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    template = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="template_variable")
    hidden = models.BooleanField(default=False)
    context = {}
    version = models.PositiveIntegerField(default=1)

    class Meta(Base.Meta):
        unique_together = ("name", "content_type")
        abstract = True
        ordering = ('name', 'content_type',)

    @property
    def var_prefix(self): 
        prefix = self.content_type.model_class().eve_variable_prefix
        version_str = "eve_tv." if self.version == 1 else f"eve_tv{self.version}."
        return f"{prefix}{version_str}"

    @property
    def var_name(self): 
        version_str = self.name if self.version == 1 else self.name+".compiled"
        return f"{self.var_prefix}{version_str}"

    @property
    def json_object(self): return { "var": self.var_name, "desc": self.description }

    def wrapper_or_none(self, tpl):
        if hasattr(self, "eve_wrapper"):
            wrp = self.eve_wrapper.split("{{ content }}")
            return wrp[0]+tpl+wrp[1]
        return tpl

    def eve_get_template_variable_compiled(self, tpl):
        return Template(self.wrapper_or_none(tpl)).render(Context(self.context))

    @property
    def compiled(self):
        return Template(self.wrapper_or_none(self.template)).render(Context(self.context))

    def pre_save(self):
        if not self.description:
            self.description = self.name