from mighty.admin.models import BaseAdmin
from mighty.applications.twofactor import fields

class TwofactorAdmin(BaseAdmin):
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.twofactor}),)
    list_display = ('code', 'user', 'mode', 'is_consumed', 'date_create', 'date_update')
    search_fields = ('user__search', 'code')
    list_filter = ('is_consumed',)
    raw_id_fields = ('user',)