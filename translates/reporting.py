from django.utils.translation import gettext as _

verbose_name = _("Reporting")
verbose_name_plural = _("Reportings")

name = _("Reporting name")
file_name = _("File name")
content_type = _("Object used to start the report ")
target = _("Object targeted by the report")
manager = _("Model manager used to get the queryset")
config = _("Configuration of the report")
filter_config = _("Filter of the report")
filter_related = _("Filter using startup object values")
is_detail = _("Filter used a specific object to start")
can_excel = _("Can export to Excel")
cfg_excel = _("Configuration of the Excel export")
can_csv = _("Can export to CSV")
cfg_csv = _("Configuration of the CSV export")
can_pdf = _("Can export to PDF")
cfg_pdf = _("Configuration of the PDF export")
html_pdf = _("HTML used to generate the PDF")
email_html = _("HTML used to generate the email")

file_name_help = _("File name will be stringified with the date of the report")
content_type_help = _("Object used to start, he can be used in filter_related")
target_help = _("Object targeted by the report, he can be used in filter_config and manager field")
manager_help = _("You can change the manager, default is 'objects'")
config_help = _("""You can config every fields used.
    - data: field name
    - label: label used in the report (not impletmented yet)
    - multiple: if the field is a multiple field, the report will use the max value to create multiple columns
    - aggregate: if the field is a multiple field, you can use a specific aggregate function
    - format: if the field is a date, you can use a specific format (not impleted yet)
    - help: help used in the report (not impleted yet)
    - width: width used in the report (not impleted yet)
    - style: style used in the report (not impleted yet)
    - class: class used (not impleted yet)""")
filter_config_help = _("""Filter used in the queryset.
example: {"field__gte": 10, "field__lte": 20}
""")
filter_related_help = _("""Filter used in the queryset using the startup object values.
example: {"target_field": "object_field"}
""")
#is_detail_help = _("")
#can_excel_help = _("")
#cfg_excel_help = _("")
#can_csv_help = _("")
#cfg_csv_help = _("")
#can_pdf_help = _("")
#cfg_pdf_help = _("")
#html_pdf_help = _("")
#email_html_help = _("")