from django.contrib import admin
from mighty.admin.models import BaseAdmin
from mighty.applications.tenant import fields

class RoleAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.role}),)

class TenantAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant}),)
    filter_horizontal = ('roles',)

class InvitationAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.invitation}),)