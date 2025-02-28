from django.contrib import admin

from mighty.applications.address import fields


class AddressAdminInline(admin.TabularInline):
    fields = fields
    extra = 0
    readonly_fields = ('addr_backend_id',)
