from django.db import models
from django.utils.module_loading import import_string
from mighty.fields import JSONField
from mighty.apps import MightyConfig
from mighty.filegenerator import FileGenerator
from mighty import translates as _

reporting_fields = (
    "export_frequency",
    "export_last_date",
    "export_email",
)

def ReportingModel(**kwargs):
    def decorator(obj):
        class ReportingModel(obj):
            export_frequency = models.CharField(_.export_frequency, max_length=25, choices=_.FREQUENCY_EXPORT, blank=True, null=True)
            export_last_date = models.DateField(_.export_last_date, auto_now=True)
            export_email = models.EmailField(_.export_email, max_length=254, blank=True, null=True)
            export_email_field = kwargs.get("email_field", "export_email")
            reporting_list = models.CharField(max_length=255, blank=True, null=True, choices=kwargs.get("reporting_list", ()))
            reporting_detail = kwargs.get("reporting_list", ())
            can_do_reporting = True

            class Meta(obj.Meta):
                abstract = True

            def file_generator(self, name, fields, items):
                return FileGenerator(filename=name, items=items, fields=fields)

            def do_reporting(self, reporting, file_type, response="http", *args, **kwargs):
                name = "reporting_%s_%s" % (reporting.lower(), file_type.lower())
                return getattr(self, name)(response) if hasattr(self, name) else False

            @property
            def email_tosend(self):
                return getattr(self, self.export_email_field)

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
