from django.contrib import admin

from mighty import translates as _


class InAlertListFilter(admin.SimpleListFilter):
    title = _.alerts
    parameter_name = 'inalert'

    def lookups(self, request, model_admin):
        return (('inalert', _.is_in_alert),)

    def queryset(self, request, queryset):
        if self.value() == 'inalert': return queryset.filter(logfields__icontains='alert')


class InErrorListFilter(admin.SimpleListFilter):
    title = _.errors
    parameter_name = 'inerror'

    def lookups(self, request, model_admin):
        return (('inerror', _.is_in_error),)

    def queryset(self, request, queryset):
        if self.value() == 'inerror': return queryset.filter(logfields__icontains='error')
