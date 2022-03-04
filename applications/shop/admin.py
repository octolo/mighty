from django.contrib import admin
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.template.response import TemplateResponse
from django.urls import resolve, path, include

from mighty.admin.models import BaseAdmin
from mighty.applications.shop import fields, translates as _
from mighty.applications.shop.apps import ShopConfig

class DiscountAdmin(BaseAdmin):
    view_on_site = False
    search_fields = ('code',)
    list_display = ('code', 'amount', 'is_percent', 'date_end')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.discount}),)

class ServiceAdmin(BaseAdmin):
    view_on_site = False
    readonly_fields = ('key',)
    search_fields = ('name', 'key')
    list_display = ('name', 'key')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.service}),)

class OfferAdmin(BaseAdmin):
    view_on_site = False
    readonly_fields = ('duration', 'named_id')
    search_fields = ('name',)
    list_display = ('name', 'frequency', 'duration')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.offer}),)
    filter_horizontal = ('service',)

class ItemAdmin(BaseAdmin):
    view_on_site = False
    search_fields = ('code',)
    list_display = ('code', 'amount', 'is_percent', 'date_end')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.discount}),)

class SubscriptionAdmin(BaseAdmin):
    change_list_template = "admin/change_list_subscription.html"
    change_form_template = "admin/change_form_subscription.html"
    view_on_site = False
    readonly_fields = (
        'next_paid',
        'bill',
        'date_start',
        'date_end',
    )
    raw_id_fields = ('group', 'offer')
    search_fields = ('group__search',)
    list_display = ('group', 'offer', 'date_start')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.subscription}),)
    filter_horizontal = ('discount',)

    def render_change_form(self, request, context, *args, **kwargs):
        if hasattr(kwargs['obj'], 'method'):
            context['adminform'].form.fields['method'].queryset = context['adminform'].form.fields['method']\
                .queryset.filter(group=kwargs['obj'].group)
        else:
            context['adminform'].form.fields['method'].queryset = context['adminform'].form.fields['method']\
                .queryset.none()
        return super(SubscriptionAdmin, self).render_change_form(request, context, *args, **kwargs)

    def exports_view(self, request, object_id=None, extra_context=None):
        current_url = resolve(request.path_info).url_name
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field) if object_id else None
        context = {
            **self.admin_site.each_context(request),
            "current_url": current_url,
            "title": "%s (%s)" % (_.exports, obj) if obj else _.exports,
            "object_name": str(opts.verbose_name),
            "object": obj,
            "opts": opts,
            "app_label": opts.app_label,
            "media": self.media
        }
        request.current_app = self.admin_site.name
        defaults = {
            "extra_context": context,
            "template_name": "admin/shop_exports.html",
        }
        from mighty.applications.shop.views import ShopExports
        return ShopExports.as_view(**defaults)(request)

    def export_view(self, request, object_id=None, extra_context=None):
        current_url = resolve(request.path_info).url_name
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field) if object_id else None
        context = {
            **self.admin_site.each_context(request),
            "current_url": current_url,
            "title": "%s (%s)" % (_.exports, obj) if obj else _.exports,
            "object_name": str(opts.verbose_name),
            "object": obj,
            "opts": opts,
            "app_label": opts.app_label,
            "media": self.media
        }
        request.current_app = self.admin_site.name
        defaults = {
            "extra_context": context,
        }
        from mighty.applications.shop.views import ShopExport
        return ShopExport.as_view(**defaults)(request)

    def dobill_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.do_bill()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/do_bill.html', context)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/dobill/', self.wrap(self.dobill_view), name='%s_%s_dobill_subscription' % info),
            path("exports/", include([
                path("", self.exports_view, name="%s_%s_exports_subscription" % info),
                path("csv/", self.export_view, name="%s_%s_export_all" % info),
            ])),

        ]
        return my_urls + urls

class BillAdmin(BaseAdmin):
    view_on_site = False
    change_form_template  = 'admin/change_form_bill.html'
    readonly_fields = ('paid', 'payment_id', 'subscription', 'method', 'date_payment', 'backend')
    search_fields = ('group__search',)
    list_display = ('group', 'paid', 'subscription')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.bill}),)
    filter_horizontal = ('discount',)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        if ShopConfig.subscription_for == 'group':
            self.readonly_fields += ('group',)
        else:
            self.readonly_fields += ('user',)

    def trytocharge_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.try_to_charge()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/try_to_charge.html', context)

    def billpdf_view(self, request, object_id=None, extra_context=None):
        current_url = resolve(request.path_info).url_name
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        pdf = obj.bill_to_pdf()
        from django.http import HttpResponse, FileResponse
        import os
        response = FileResponse(open(pdf, 'rb'), filename=obj.bill_pdf_name)
        os.remove(pdf)
        return response

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/pdf/', self.billpdf_view, name='%s_%s_pdf_bill' % info),
            path('<path:object_id>/trytocharge/', self.wrap(self.trytocharge_view), name='%s_%s_trytocharge_bill' % info),
        ]
        return my_urls + urls

class PaymentMethodAdmin(BaseAdmin):
    view_on_site = False
    raw_id_fields = ('group',)
    readonly_fields = ('backend', 'service_id', 'service_detail')
    search_fields = ('group__search',)
    list_display = ('group', 'form_method', 'date_valid')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.method}),)

class SubscriptionRequestAdmin(BaseAdmin):
    view_on_site = False
    raw_id_fields = ('offer', 'user')
    readonly_fields = ('backend', 'service_id', 'service_detail')
    search_fields = ('group__search',)
    list_display = ('user', 'offer', 'form_method',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.subscription_request}),)

class SubscriptionAdminInline(admin.StackedInline):
    raw_id_fields = ('group', 'offer')
    readonly_fields = (
        'next_paid',
        'bill',
        'discount',
        'date_start',
        'date_end',
    )
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.subscription}),)
    extra = 0
