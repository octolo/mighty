
from mighty.admin.models import BaseAdmin
from mighty.applications.nationality.fields import searchs

class NationalityAdmin(BaseAdmin):
    view_on_site = False
    list_display = ('country', 'image_html', 'alpha2', 'alpha3', 'numeric')
    fieldsets = ((None, {'classes': ('wide',), 'fields': searchs}),)