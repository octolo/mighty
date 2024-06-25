from mighty.admin.models import BaseAdmin
from mighty.applications.tenant import fields

class RoleAdmin(BaseAdmin):
    raw_id_fields = ('group', )
    view_on_site = False
    search_fields = ('name', 'group__search')
    list_display = ('name', 'is_immutable', 'group')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.role}),)
    readonly_fields = ('number', 'three_first')

class TenantAdmin(BaseAdmin):
    raw_id_fields = ('group', 'user')
    search_fields = ('group__search', 'user__search')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant}),)
    filter_horizontal = ('roles',)

    def render_change_form(self, request, context, *args, **kwargs):
        if hasattr(kwargs['obj'], 'roles'):
            context['adminform'].form.fields['roles'].queryset = context['adminform'].form.fields['roles']\
                .queryset.filter(group=kwargs['obj'].group)
        else:
            context['adminform'].form.fields['roles'].queryset = context['adminform'].form.fields['roles']\
                .queryset.none()
        return super(TenantAdmin, self).render_change_form(request, context, *args, **kwargs)
