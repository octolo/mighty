from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote

from mighty.admin.models import BaseAdmin
from mighty.applications.messenger import fields

class MissiveAdmin(BaseAdmin):
    change_form_template  = 'admin/change_form_missives.html'
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.missive}),)
    list_display = ('target', 'subject', 'mode', 'status')
    search_fields = ('target',)
    list_filter = ('mode', 'status')
    readonly_fields = ('backend', 'response')

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
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/missive.html', context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/html/', self.wrap(self.html_view), name='%s_%s_html' % info),
        ]
        return my_urls + urls 