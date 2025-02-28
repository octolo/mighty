from django.db import models

from mighty import translates as _
from mighty.filegenerator import FileGenerator

reporting_fields = (
    'reporting_frequency',
    'reporting_task_date',
    'reporting_email',
)


def ReportingModel(**kwargs):
    def decorator(obj):
        class NewClass(obj):
            reporting_frequency = models.CharField(
                _.reporting_frequency,
                max_length=25,
                choices=_.FREQUENCY_EXPORT,
                blank=True,
                null=True,
            )
            reporting_task_date = models.JSONField(
                default=dict, blank=True, null=True
            )
            reporting_email = models.EmailField(
                _.reporting_email, max_length=254, blank=True, null=True
            )
            reporting_email_field = kwargs.get('email_field', 'reporting_email')
            reporting_list = models.CharField(
                max_length=255,
                blank=True,
                null=True,
                choices=kwargs.get('reporting_list', ()),
            )
            reporting_detail = kwargs.get('reporting_list', ())
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
                return self.get_url(
                    'reporting', self.app_admin, arguments=self.admin_url_args
                )

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
            def reporting_definition(self):
                rc = [
                    {
                        'id': 'std:' + k,
                        'name': v,
                        'excel': True,
                        'csv': True,
                        'pdf': False,
                        'is_detail': True,
                    }
                    for k, v in dict(self.reporting_detail).items()
                ]
                rc += [
                    {
                        'id': 'cfg:' + str(rpg.uid),
                        'name': rpg.name,
                        'excel': rpg.can_excel,
                        'xlsx': rpg.can_excel,
                        'csv': rpg.can_csv,
                        'pdf': rpg.can_pdf,
                        'is_detail': rpg.is_detail,
                    }
                    for rpg in self.reporting_qs
                ]
                return rc

            @property
            def reporting_choices(self):
                rc = [
                    ('std:' + k, v)
                    for k, v in dict(self.reporting_detail).items()
                ]
                rc += [
                    ('cfg:' + str(rpg.uid), rpg.name)
                    for rpg in self.reporting_qs
                ]
                return rc

            def reporting_file_generator(self, name, fields, items):
                return FileGenerator(filename=name, items=items, fields=fields)

            def reporting_process_cfg(
                self, reporting, file_type, response='http', *args, **kwargs
            ):
                reporting = self.reporting_qs.get(uid=reporting)
                reporting.related_obj = self
                reporting.email_target = kwargs.get('email_target')
                return reporting.reporting_file_response(
                    response, file_type, *args, **kwargs
                )

            def reporting_process_std(
                self, reporting, file_type, response='http', *args, **kwargs
            ):
                file_type = (
                    'xlsx'
                    if file_type.lower() == 'excel'
                    else file_type.lower()
                )
                name = f'reporting_{reporting.lower()}_{file_type}'
                return (
                    getattr(self, name)(response)
                    if hasattr(self, name)
                    else False
                )

            def reporting_process(
                self, spec, reporting, file_type, *args, **kwargs
            ):
                return getattr(self, 'reporting_process_' + spec)(
                    reporting, file_type, *args, **kwargs
                )

            def reporting_execute(self, request=None, *args, **kwargs):
                reporting = kwargs.pop(
                    'reporting', request.GET.get('reporting', None)
                )
                file_type = kwargs.pop(
                    'file_type', request.GET.get('file_type', 'csv')
                )
                if reporting:
                    spec, reporting = reporting.split(':')
                    return self.reporting_process(
                        spec, reporting, file_type, *args, **kwargs
                    )
                return None

        NewClass.__name__ = obj.__name__
        return NewClass

    return decorator
