from django.db import models
from django.utils.module_loading import import_string
from mighty.fields import JSONField
from mighty.apps import MightyConfig
from mighty.filegenerator import FileGenerator
from mighty import translates as _

reporting_fields = ("reporting_frequency", "reporting_last_date", "reporting_email")

def ReportingModel(**kwargs):
    def decorator(obj):
        class ReportingModel(obj):
            reporting_frequency = models.CharField(_.reporting_frequency, max_length=25, choices=_.FREQUENCY_EXPORT, blank=True, null=True)
            reporting_last_date = models.DateField(_.reporting_last_date, auto_now=True)
            reporting_email = models.EmailField(_.reporting_email, max_length=254, blank=True, null=True)
            reporting_email_field = kwargs.get("email_field", "reporting_email")
            reporting_list = models.CharField(max_length=255, blank=True, null=True, choices=kwargs.get("reporting_list", ()))
            reporting_detail = kwargs.get("reporting_list", ())
            reporting_enable = True

            class Meta(obj.Meta):
                abstract = True

            @property
            def reporting_keys(self):
                return dict(self.reporting_detail).keys()

            @property
            def reporting_json(self):
                return dict(self.reporting_detail)

            @property
            def reporting_admin_url(self):
                return self.get_url('reporting', self.app_admin, arguments=self.admin_url_args)

            @property
            def reporting_send_to_email(self):
                return getattr(self, self.reporting_email_field)

            @property
            def reporting_form(self):
                from mighty.forms import ReportingForm
                class ReportingForm(ReportingForm):
                    class Meta:
                        model = type(self)
                        fields = ()
                return ReportingForm()

            @property
            def reporting_qs(self):
                ct = self.get_content_type()
                return ct.ct_to_reporting.all()

            @property
            def reporting_choices(self):
                rc = [("std:"+k, v) for k,v in dict(self.reporting_detail).items()]
                rc += [("cfg:"+str(rpg.uid), rpg.name) for rpg in self.reporting_qs]
                return rc

            def reporting_file_generator(self, name, fields, items):
                return FileGenerator(filename=name, items=items, fields=fields)

            def reporting_process_cfg(self, reporting, file_type, response="http", *args, **kwargs):
                reporting = self.reporting_qs.get(uid=reporting)
                return reporting.reporting_file_response(response, file_type)

            def reporting_process_std(self, reporting, file_type, response="http", *args, **kwargs):
                name = "reporting_%s_%s" % (reporting.lower(), file_type.lower())
                return getattr(self, name)(response) if hasattr(self, name) else False

            def reporting_process(self, spec, reporting, file_type, *args, **kwargs):
                return getattr(self, "reporting_process_"+spec)(reporting, file_type, *args, **kwargs)

            def reporting_execute(self, request, *args, **kwargs):
                reporting = request.POST.get("reporting")
                file_type = request.POST.get("file_type", "csv")
                if reporting:
                    spec, reporting = reporting.split(":")
                    return self.reporting_process(spec, reporting, file_type, *args, **kwargs)

        return ReportingModel
    return decorator
