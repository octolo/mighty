from django.contrib import admin
from mighty.admin.models import BaseAdmin
from mighty.applications.signature import fields

class TransactionDocumentInline(admin.StackedInline):
    fields = fields.document
    extra = 0

class TransactionSignatoryInline(admin.StackedInline):
    fields = fields.signatory
    extra = 0

class TransactionLocationInline(admin.StackedInline):
    fields = fields.location
    extra = 0

class TransactionAdmin(BaseAdmin):
    view_on_site = False
    search_fields = ('name', 'search')
    list_display = ('name',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.transaction}),)
    readonly_fields = ()

class TransactionDocumentAdmin(BaseAdmin):
    raw_id_fields = ('transaction',)
    view_on_site = False
    search_fields = ('search',)
    list_display = ('__str__',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.document}),)
    readonly_fields = ()

class TransactionSignatoryAdmin(BaseAdmin):
    raw_id_fields = ('transaction', 'signatory')
    view_on_site = False
    search_fields = ('search',)
    list_display = ('__str__',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.signatory}),)
    readonly_fields = ()

class TransactionLocationAdmin(BaseAdmin):
    raw_id_fields = ('transaction', 'signatory', 'document')
    view_on_site = False
    search_fields = ('search',)
    list_display = ('__str__',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.location}),)
    readonly_fields = ()