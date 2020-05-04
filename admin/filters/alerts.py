from django.contrib import admin
from mighty.translates import descriptions, fields

class InAlertListFilter(admin.SimpleListFilter):
    title = fields.alerts
    parameter_name = 'inalert'

    def lookups(self, request, model_admin):
        return (('inalert', descriptions.is_in_alert),)

    def queryset(self, request, queryset):
        if self.value() == 'inalert': return queryset.filter(alerts__isnull=False)