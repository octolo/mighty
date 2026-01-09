from django.contrib import messages
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.urls import path

from mighty.admin.models import BaseAdmin
from mighty.applications.address import fields as addr_fields
from mighty.applications.messenger import fields, forms


class MissiveAdmin(BaseAdmin):
    view_on_site = False
    list_display = ('target', 'subject', 'mode', 'status', 'date_create')
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

    viewer_view_template = 'admin/missive/viewer.html'
    viewer_view_suffix = 'viewer'
    viewer_view_path = '<path:object_id>/viewer/'
    viewer_view_object_tools = {'name': 'Viewer', 'url': 'viewer'}

    def viewer_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        missive = self.get_object(request, unquote(object_id), to_field)
        extra_context['object'] = missive
        request.current_app = self.admin_site.name
        return self.admincustom_view(
            request,
            object_id,
            extra_context,
            urlname=self.get_admin_urlname(self.check_view_suffix),
            template=self.viewer_view_template,
        )

    check_view_template = 'admin/missive/check.html'
    check_view_suffix = 'check'
    check_view_path = '<path:object_id>/check/'
    check_view_object_tools = {'name': 'Check', 'url': 'check'}

    def check_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        missive = self.get_object(request, unquote(object_id), to_field)

        if 'proof' in request.GET:
            proof_key = request.GET['proof']
            return missive.download_proof(proof=proof_key, http_response=True)

        # status
        missive_status = missive.check_status()
        extra_context.update({'missive_status': missive_status})

        # documents
        missive_documents = missive.check_documents()
        extra_context.update({'missive_documents': missive_documents})

        # invoice
        missive_invoice = missive.get_invoice()
        extra_context['missive_invoice'] = missive_invoice

        # proofs
        missive_proofs = missive.get_prooflist()
        extra_context['missive_proofs'] = missive_proofs

        return self.admincustom_view(
            request,
            object_id,
            extra_context,
            urlname=self.get_admin_urlname(self.check_view_suffix),
            template=self.check_view_template,
        )

    missivecancel_view_template = 'admin/missive/cancel.html'
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

    reporting_view_template = 'admin/missive/reporting.html'
    reporting_view_suffix = 'reporting'
    reporting_view_path = 'reporting/'
    reporting_view_object_tools = {
        'name': 'Reporting',
        'url': 'reporting',
        'list': True,
    }

    def reporting_view(
        self, request, object_id=None, form_url=None, extra_context=None
    ):
        extra_context = extra_context or {}
        generate_form = forms.MissiveReportingForm(
            request.POST or None, request.FILES or None
        )
        extra_context['form'] = generate_form
        if generate_form.is_valid():
            generate_form.generate_report()
            extra_context['form_valid'] = True
            messages.success(request, 'Report generated successfully.')
        return self.admincustom_view(
            request,
            object_id,
            extra_context,
            urlname=self.get_admin_urlname(self.reporting_view_suffix),
            template=self.reporting_view_template,
        )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                self.viewer_view_path,
                self.wrap(
                    self.viewer_view,
                    object_tools=self.viewer_view_object_tools,
                ),
                name=self.get_admin_urlname(self.viewer_view_suffix),
            ),
            path(
                self.check_view_path,
                self.wrap(
                    self.check_view,
                    object_tools=self.check_view_object_tools,
                ),
                name=self.get_admin_urlname(self.check_view_suffix),
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
