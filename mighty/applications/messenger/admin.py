from mighty.admin.models import BaseAdmin
from mighty.applications.messenger import fields

class MissiveAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.missive}),)
    list_display = ('target', 'subject', 'mode', 'status')
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = ('backend', 'response')