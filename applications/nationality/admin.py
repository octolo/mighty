
from mighty.admin.models import BaseAdmin
from mighty.applications.nationality.fields import searchs

class NationalityAdmin(BaseAdmin):
    view_on_site = False
    list_display = ('country', 'alpha2', 'alpha3', 'numeric', 'image_html')
    fieldsets = ((None, {'classes': ('wide',), 'fields': searchs}),)