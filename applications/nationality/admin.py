
from mighty.admin.models import BaseAdmin
from mighty.applications.grapher import fields, translates as _

class NationalityAdmin(BaseAdmin):
    list_display = ('country', 'alpha2', 'alpha3', 'numeric', 'image_html')