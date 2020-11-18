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

class TenantAlternateAdmin(admin.StackedInline):
    raw_id_fields = ('user',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant_alternate}),)
    readonly_fields = ('invitation',)
    extra = 0

class TenantInvitationAdmin(BaseAdmin):
    raw_id_fields = ('group', 'by', 'tenant')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant_invitation + ('missive_link',)}),)
    filter_horizontal = ('roles',)
    readonly_fields = ('missive_link',)

    def missive_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        link = reverse("admin:mighty_missive_change", args=[obj.missive.id])
        return format_html('<a href="{}">{}</a>', link, obj.missive) if obj.missive else None
    missive_link.short_description = 'Missive'