from django.contrib import admin
from mighty.admin.models import BaseAdmin
from mighty.applications.tenant import fields

class RoleAdmin(BaseAdmin):
    view_on_site = False
    search_fields = ('name', 'group__search')
    list_display = ('name', 'is_immutable', 'group')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.role}),)

class TenantAdmin(BaseAdmin):
    raw_id_fields = ('group', 'user')
    search_fields = ('email', 'group__search', 'user__search')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant}),)
    filter_horizontal = ('roles',)
    readonly_fields = ('invitation',)

class TenantAlternateAdmin(admin.StackedInline):
    fk_name = 'tenant'
    raw_id_fields = ('tenant', 'alternate')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant_alternate}),)
    extra = 1

class TenantInvitationAdmin(BaseAdmin):
    raw_id_fields = ('group', 'by', 'tenant')
    search_fields = ('email', 'group__search', 'user__search')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant_invitation + ('missive_link',)}),)
    filter_horizontal = ('roles',)
    readonly_fields = ('missive_link', 'token')

    def missive_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        link = reverse("admin:mighty_missive_change", args=[obj.missive.id])
        return format_html('<a href="{}">{}</a>', link, obj.missive) if obj.missive else None
    missive_link.short_description = 'Missive'