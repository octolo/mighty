from django.contrib import admin
from mighty.applications.address import fields

class AddressAdminInline(admin.TabularInline):
    fields = fields
    extra = 0
