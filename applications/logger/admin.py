from django.template.response import TemplateResponse
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.core.paginator import Paginator
from mighty.admin.models import BaseAdmin
from mighty.applications.logger import fields
from mighty.models import Log


class LogAdmin(BaseAdmin):
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.log}),)
    list_display = ('msg', 'log_hash')
    search_fields = ('msg', 'log_hash')
    list_filter = ("content_type",)
    readonly_fields = fields.log

class ModelChangeLogAdmin(BaseAdmin):
    change_form_template  = 'admin/change_form_modelchangelog.html'
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.modelchangelog}),)
    list_display = fields.modelchangelog
    list_filter = ("content_type", "date_begin", "date_end")
    search_fields = ('object_id', 'field', 'value')
    readonly_fields = fields.modelchangelog

class ModelWithLogAdmin(BaseAdmin):
    change_form_template  = 'admin/change_form_logs.html'

    def logs_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        try:
            ctype = ContentType.objects.get(app_label=obj.app_label, model=obj.model_name)
            logs = Log.objects.filter(content_type=ctype, object_id=obj.id)
        except ContentType.DoesNotExist:
            logs = None
        except Log.DoesNotExist:
            logs = None
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'fake': Log(),
            'logs': logs,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/logs.html', context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/logs/', self.wrap(self.logs_view), name='%s_%s_logs' % info),
        ]
        return my_urls + urls
