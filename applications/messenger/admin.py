from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.template.response import TemplateResponse
from django.http import FileResponse

from mighty.admin.models import BaseAdmin
from mighty.applications.address import fields as addr_fields
from mighty.applications.messenger import fields, forms


class MissiveAdmin(BaseAdmin):
    change_form_template = 'admin/change_form_missives.html'
    view_on_site = False
    list_display = ('target', 'subject', 'mode', 'status')
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = (
        'backend',
        'addr_backend_id',
        'response',
        'partner_id',
        'code_error',
        'trace',
        'admin_url_html',
    )
    fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'backend',
                    'mode',
                    'status',
                    'name',
                    'sender',
                    'reply',
                    'reply_name',
                    'target',
                ),
            },
        ),
        (
            'Content type',
            {
                'classes': ('wide',),
                'fields': (
                    'admin_url_html',
                    'content_type',
                    'object_id',
                ),
            },
        ),
        (
            'Contact',
            {
                'classes': ('collapse',),
                'fields': (
                    'denomination',
                    'last_name',
                    'first_name',
                ),
            },
        ),
        ('Address', {'classes': ('collapse',), 'fields': addr_fields}),
        (
            'Content',
            {
                'classes': ('collapse',),
                'fields': (
                    'subject',
                    'template',
                    'header_html',
                    'footer_html',
                    'preheader',
                    'html',
                    'txt',
                ),
            },
        ),
        (
            'Follow',
            {
                'classes': ('collapse',),
                'fields': (
                    'response',
                    'msg_id',
                    'partner_id',
                    'trace',
                    'code_error',
                ),
            },
        ),
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

    def check_documents(self, request, object_id, extra_context=None):
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
            'callback': obj.check_documents(),
            'js_admin': obj.js_admin,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/missive_check.html', context)

    missivecancel_view_template = 'admin/missivecancel.html'
    missivecancel_view_suffix = 'missivecancel'
    missivecancel_view_path = '<path:object_id>/missivecancel/'
    missivecancel_view_object_tools = {'name': 'Cancel', 'url': 'missivecancel'}

    def missivecancel_view(
        self, request, object_id, form_url=None, extra_context=None
    ):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        extra_context = {'response': obj.cancel_missive()}
        return self.admincustom_view(
            request,
            object_id,
            extra_context,
            urlname=self.get_admin_urlname(self.missivecancel_view_suffix),
            template=self.missivecancel_view_template,
        )

    reporting_view_template = 'admin/reporting_missive.html'
    reporting_view_suffix = 'reporting'
    reporting_view_path = 'reporting/'
    reporting_view_object_tools = {'name': 'Reporting', 'url': 'reporting', 'list': True}

    def reporting_view(self, request, object_id=None, form_url=None, extra_context=None):
        extra_context = extra_context or {}
        generate_form = forms.MissiveReportingForm(request.POST or None, request.FILES or None)
        extra_context['form'] = generate_form
        if generate_form.is_valid():
            generate_form.generate_report()
        return self.admincustom_view(
            request,
            object_id,
            extra_context,
            urlname=self.get_admin_urlname(self.reporting_view_suffix),
            template=self.reporting_view_template,
        )

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path(
                '<path:object_id>/html/',
                self.wrap(self.html_view),
                name='{}_{}_html'.format(*info),
            ),
            path(
                '<path:object_id>/check/',
                self.wrap(self.check_view),
                name='{}_{}_check'.format(*info),
            ),
            path(
                '<path:object_id>/documents/',
                self.wrap(self.check_documents),
                name='{}_{}_documents'.format(*info),
            ),
            path(
                self.missivecancel_view_path,
                self.wrap(
                    self.missivecancel_view,
                    object_tools=self.missivecancel_view_object_tools,
                ),
                name=self.get_admin_urlname(self.missivecancel_view_suffix),
            ),
            path(
                self.reporting_view_path,
                self.wrap(
                    self.reporting_view,
                    object_tools=self.reporting_view_object_tools,
                ),
                name=self.get_admin_urlname(self.reporting_view_suffix),
            ),
        ]
        return my_urls + urls


class NotificationAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.notification}),)
    list_display = ('target', 'subject', 'mode')
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = ('missive',)


class NotificationAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.notification}),)
    list_display = ('target', 'subject', 'mode')
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = ('missive',)


class TemplateAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.template}),)
    search_fields = ('code',)
