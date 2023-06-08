from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote

from mighty.admin.models import BaseAdmin
from mighty.applications.messenger import fields
from mighty.applications.address import fields as addr_fields

class MissiveAdmin(BaseAdmin):
    change_form_template  = 'admin/change_form_missives.html'
    view_on_site = False
    list_display = ('target', 'subject', 'mode', 'status')
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = ('backend', 'addr_backend_id', 'response', 'partner_id', 'code_error', 'trace')
    fieldsets = (
        (None, {"classes": ("wide",), "fields": (
            "mode",
            "status",
            "name",
            "sender",
            "reply",
            "reply_name",
            "target",
            "denomination",
            "last_name",
            "first_name",
        )}),
        ("Address", {"classes": ("wide",), "fields": addr_fields}),
        ("Content", {"classes": ("collapse",), "fields": (
            "subject",
            "template",
            "header_html",
            "footer_html",
            "preheader",
            "html",
            "txt",
        )}),
        ("Follow", {"classes": ("wide",), "fields": (
            "content_type",
            "object_id",
            "backend",
            "response",
            "msg_id",
            "partner_id",
            "trace",
            "code_error",
        )}),
    )

    def html_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/missive.html', context)

    def check_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
            'callback': obj.check_status(),
            'js_admin': obj.js_admin,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/missive_check.html', context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/html/', self.wrap(self.html_view), name='%s_%s_html' % info),
            path('<path:object_id>/check/', self.wrap(self.check_view), name='%s_%s_check' % info),
        ]
        return my_urls + urls

class NotificationAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.notification}),)
    list_display = ('target', 'subject', 'mode',)
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = ('missive',)


class NotificationAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.notification}),)
    list_display = ('target', 'subject', 'mode',)
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = ('missive',)

class TemplateAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.template}),)
    search_fields = ('code',)
