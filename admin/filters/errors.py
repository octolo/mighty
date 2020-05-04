from django.contrib import admin
from mighty.translates import descriptions, fields

class InErrorListFilter(admin.SimpleListFilter):
    title = fields.errors
    parameter_name = 'inerror'

    def lookups(self, request, model_admin):
        return (('inerror', descriptions.is_in_error),)

    def queryset(self, request, queryset):
        if self.value() == 'inerror': return queryset.filter(errors__isnull=False)