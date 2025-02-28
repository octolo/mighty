from mighty.admin.models import BaseAdmin
from mighty.applications.dataprotect import fields


class ServiceDataAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.servicedata}),)
    list_display = ('name', 'category')


class UserDataProtectAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = (
        (None, {'classes': ('wide',), 'fields': fields.userdataprotect}),
    )
    list_display = ('session_id', 'user')
