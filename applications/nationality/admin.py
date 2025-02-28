from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from mighty.admin.models import BaseAdmin
from mighty.applications.nationality import fields
from mighty.fields import JSONField


class NationalityAdmin(BaseAdmin):
    view_on_site = False
    list_display = ('country', 'alpha2', 'alpha3', 'numeric')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.nationality}),)


class TranslateDictAdmin(admin.StackedInline):
    formfield_overrides = {JSONField: {'widget': JSONEditorWidget}}
    fields = fields.translatedict
    extra = 0


class TranslatorAdmin(BaseAdmin):
    change_list_template = 'admin/translate_change_list.html'
    view_on_site = False
    list_display = ('name',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('name',)}),)

    # @never_cache
    def csv_view(self, request, object_id=None, extra_context=None):
        from mighty.filegenerator import FileGenerator
        from mighty.models import TranslateDict

        items = []
        for td in TranslateDict.objects.all():
            for key, tr in td.one_dim_format.items():
                items.append([key, tr])
        fg = FileGenerator(
            filename='exporttr', items=items, fields=('path', 'translation')
        )
        return fg.response_http('csv')
        # import csv
        # from django.http import StreamingHttpResponse
        # response = HttpResponse(
        #    content_type='text/csv',
        #    headers={'Content-Disposition': 'attachment; filename="somefilename.csv"'},
        # )

    #    writer = csv.writer(response)
    #    writer.writerow(['path', 'translation'])
    #    from mighty.models import TranslateDict
    #    tds = {}
    #    for td in TranslateDict.objects.all():
    #        for key,tr in td.one_dim_format.items():
    #            writer.writerow([key, tr])
    #    return response

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        my_urls = [
            path(
                'export/csv/',
                self.csv_view,
                name='translators_admin_export_csv',
            ),
        ]
        return my_urls + urls
