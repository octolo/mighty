from django.contrib import admin
from mighty.admin.models import BaseAdmin
from mighty.applications.tenant import fields

class RoleAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.role}),)

class TenantAdmin(BaseAdmin):
    raw_id_fields = ('group', 'user')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant}),)
    filter_horizontal = ('roles',)
    readonly_fields = ('invitation',)


class TenantInvitationAdmin(BaseAdmin):
    raw_id_fields = ('group', 'tenant', 'by')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant_invitation}),)
    filter_horizontal = ('roles',)
    readonly_fields = ('invitation',)