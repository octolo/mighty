from mighty.admin.models import BaseAdmin
from mighty.applications.tenant import fields

class TenantAdmin(BaseAdmin):
    raw_id_fields = ('group', 'user')
    search_fields = ('group__search', 'user__search')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant}),)
    filter_horizontal = ()
