from django.contrib import admin
from mighty.admin.models import BaseAdmin
from mighty.applications.tenant import fields

class RoleAdmin(BaseAdmin):
    view_on_site = False
    search_fields = ('name', 'group__search')
    list_display = ('name', 'is_immutable', 'group')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.role}),)
    readonly_fields = ('number',)

class TenantAdmin(BaseAdmin):
    raw_id_fields = ('group', 'user')
    search_fields = ('tenant_invitation__email', 'group__search', 'user__search')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant}),)
    filter_horizontal = ('roles',)
    readonly_fields = ('invitation',)

    def render_change_form(self, request, context, *args, **kwargs):
        if hasattr(kwargs['obj'], 'roles'):
            context['adminform'].form.fields['roles'].queryset = context['adminform'].form.fields['roles']\
                .queryset.filter(group=kwargs['obj'].group)
        else:
            context['adminform'].form.fields['roles'].queryset = context['adminform'].form.fields['roles']\
                .queryset.none()
        return super(TenantAdmin, self).render_change_form(request, context, *args, **kwargs)

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