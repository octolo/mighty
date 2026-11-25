from django.contrib.admin.utils import quote
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html, format_html_join
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from mighty.admin.models import BaseAdmin
from mighty.applications.tenant import fields


class RoleAdmin(BaseAdmin):
    raw_id_fields = ('group',)
    view_on_site = False
    search_fields = ('name', 'group__search')
    list_display = ('name', 'is_immutable', 'group')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.role}),)


class TenantAdmin(BaseAdmin):
    raw_id_fields = ('group', 'user')
    search_fields = ('group__search', 'user__search')
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.tenant}),)
    filter_horizontal = ('roles',)
    readonly_fields = ('related_objects',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None or not self.has_related_objects(obj):
            return fieldsets
        return (
            *fieldsets,
            (_('Related objects'), {'fields': ('related_objects',)}),
        )

    def get_reverse_foreign_keys(self, obj):
        return tuple(
            relation
            for relation in obj._meta.get_fields()
            if relation.auto_created
            and not relation.concrete
            and relation.one_to_many
        )

    def has_related_objects(self, obj):
        return any(
            getattr(obj, relation.get_accessor_name()).exists()
            for relation in self.get_reverse_foreign_keys(obj)
        )

    def related_objects(self, obj):
        return format_html_join(
            '',
            '<div>{} - {}</div>',
            (
                (
                    capfirst(relation.related_model._meta.verbose_name),
                    self.related_object_link(related_object),
                )
                for relation in self.get_reverse_foreign_keys(obj)
                for related_object in getattr(
                    obj, relation.get_accessor_name()
                ).all()
            ),
        )

    def related_object_link(self, related_object):
        options = related_object._meta
        try:
            url = reverse(
                f'{self.admin_site.name}:{options.app_label}_'
                f'{options.model_name}_change',
                args=(quote(str(related_object.pk)),),
            )
        except NoReverseMatch:
            return str(related_object)
        return format_html('<a href="{}">{}</a>', url, related_object)

    related_objects.short_description = _('Related objects')

    def render_change_form(self, request, context, *args, **kwargs):
        if hasattr(kwargs['obj'], 'roles'):
            context['adminform'].form.fields['roles'].queryset = (
                context['adminform']
                .form.fields['roles']
                .queryset.filter(group=kwargs['obj'].group)
            )
        else:
            context['adminform'].form.fields['roles'].queryset = (
                context['adminform'].form.fields['roles'].queryset.none()
            )
        return super().render_change_form(request, context, *args, **kwargs)
