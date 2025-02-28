from mighty.admin.models import BaseAdmin
from mighty.applications.twofactor import fields


class TwofactorAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.twofactor}),)
    list_display = ('code', 'user', 'email_or_phone', 'mode', 'is_consumed', 'date_create', 'date_update')
    search_fields = ('user__search', 'code')
    list_filter = ('is_consumed',)
    readonly_fields = fields.twofactor
    raw_id_fields = ('user',)
