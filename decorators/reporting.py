from django.db import models
from django.utils.module_loading import import_string
from mighty.fields import JSONField
from mighty.apps import MightyConfig
from mighty.filegenerator import FileGenerator

def ReportingModel(**kwargs):
    def decorator(obj):
        class ReportingModel(obj):
            reporting_list = models.CharField(max_length=255, blank=True, null=True, choices=kwargs.get("reporting_list", ()))
            can_do_reporting = True

            class Meta(obj.Meta):
                abstract = True

            def file_generator(self, name, fields, items):
                return FileGenerator(filename=name, items=items, fields=fields)

            def do_reporting(self, reporting, file_type, *args, **kwargs):
                name = "reporting_%s_%s" % (reporting.lower(), file_type.lower())
                return getattr(self, name)() if hasattr(self, name) else False

            @property
            def form_reporting(self):
                from mighty.forms import ReportingForm
                class ReportingForm(ReportingForm):
                    class Meta:
                        model = type(self)
                        fields = ("reporting_list",)
                return ReportingForm()

            @property
            def admin_reporting_url(self): return self.get_url('reporting', self.app_admin, arguments=self.admin_url_args)

        return ReportingModel
    return decorator
