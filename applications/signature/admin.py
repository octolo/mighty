from django.contrib import admin
from mighty.admin.models import BaseAdmin
from mighty.applications.signature import fields

class TransactionDocumentInline(admin.StackedInline):
    fields = fields.document
    extra = 0

class TransactionSignatoryInline(admin.StackedInline):
    fields = fields.signatory
    extra = 0

class TransactionAdmin(BaseAdmin):
    view_on_site = False
    search_fields = ('name', 'search')
    list_display = ('name',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.transaction}),)
    readonly_fields = ()
