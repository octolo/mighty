from django.contrib import admin
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.urls import reverse, resolve

from mighty.admin.models import BaseAdmin
from mighty.applications.shop import fields, translates as _

class ServiceAdmin(BaseAdmin):
    view_on_site = False
    readonly_fields = ('code',)
    search_fields = ('name', 'code')
    list_display = ('name', 'code')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.service}),)

class OfferAdmin(BaseAdmin):
    view_on_site = False
    readonly_fields = ('duration',)
    search_fields = ('name',)
    list_display = ('name', 'frequency', 'duration')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.offer}),)
    filter_horizontal = ('service',)

class SubscriptionAdmin(BaseAdmin):
    change_list_template = "admin/subscription_change_list.html"
    view_on_site = False
    readonly_fields = (
        'next_paid',
        'bill',
        'discount',
        'date_start',
        'date_end',
    )
    raw_id_fields = ('group', 'offer')
    search_fields = ('group__search',)
    list_display = ('group', 'offer', 'date_start')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.subscription}),)

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


    def get_urls(self):
        from django.urls import path, include
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path("exports/", include([
                path("", self.exports_view, name="%s_%s_exports_subscription" % info),
                path("csv/", self.export_view, name="%s_%s_export_all" % info),
            ])),

        ]
        return my_urls + urls

class BillAdmin(BaseAdmin):
    view_on_site = False
    readonly_fields = ('paid', 'payment_id', 'subscription', 'method', 'date_payment')
    search_fields = ('group__search',)
    list_display = ('group', 'paid', 'subscription')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.bill}),)

class DiscountAdmin(BaseAdmin):
    view_on_site = False
    list_display = ('code', 'amount', 'is_percent')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.discount}),)

class PaymentMethodAdmin(BaseAdmin):
    view_on_site = False
    readonly_fields = ('backend', 'service_id', 'service_detail')
    search_fields = ('group__search',)
    list_display = ('group', 'form_method')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.payment_method}),)

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

class SubscriptionGroupAdmin(BaseAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.add_field('Informations', fields.subscription_group)
        self.readonly_fields += fields.subscription_group
