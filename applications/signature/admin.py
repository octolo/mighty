from django.contrib import admin
from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.urls import path

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
    change_form_template  = 'admin/change_form_transaction.html'
    view_on_site = False
    search_fields = ('name', 'search')
    list_display = ('name',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.transaction}),)
    readonly_fields = ()

    def starttransaction_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.start_transaction()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/start_transaction.html', context)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/starttransaction/', self.wrap(self.starttransaction_view), name='%s_%s_starttransaction' % info),
        ]
        return my_urls + urls 

class TransactionDocumentAdmin(BaseAdmin):
    change_form_template  = 'admin/change_form_document.html'
    raw_id_fields = ('transaction',)
    view_on_site = False
    search_fields = ('search',)
    list_display = ('__str__',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.document}),)
    readonly_fields = ()

    def addtransaction_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.add_to_transaction()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/add_document_transaction.html', context)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/addtransaction/', self.wrap(self.addtransaction_view), name='%s_%s_addtransaction' % info),
        ]
        return my_urls + urls 

class TransactionSignatoryAdmin(BaseAdmin):
    change_form_template  = 'admin/change_form_signatory.html'
    raw_id_fields = ('transaction', 'signatory')
    view_on_site = False
    search_fields = ('search',)
    list_display = ('__str__',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.signatory}),)
    readonly_fields = ()

    def addtransaction_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.add_to_transaction()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/add_signatory_transaction.html', context)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/addtransaction/', self.wrap(self.addtransaction_view), name='%s_%s_addtransaction' % info),
        ]
        return my_urls + urls 

class TransactionLocationAdmin(BaseAdmin):
    change_form_template  = 'admin/change_form_location.html'
    raw_id_fields = ('transaction', 'signatory', 'document')
    view_on_site = False
    search_fields = ('search',)
    list_display = ('__str__',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.location}),)
    readonly_fields = ()

    def addtransaction_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.add_to_transaction()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/add_location_transaction.html', context)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/addtransaction/', self.wrap(self.addtransaction_view), name='%s_%s_addtransaction' % info),
        ]
        return my_urls + urls 