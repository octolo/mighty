from django.contrib import admin
from mighty.admin.models import BaseAdmin
from mighty.applications.dataprotect import fields
from mighty.models import ServiceData, UserDataProtect

class ServiceDataAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.servicedata}),)
    list_display = ('name', 'level')

class UserDataProtectAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.userdataprotect}),)
    list_display = ('user', 'nbr_accept', 'nbr_refuse')