from django.http import StreamingHttpResponse
from django.views.generic.base import RedirectView
from mighty.views.base import BaseView
from mighty.views.crud import ListView, DetailView
import csv

# Buffer for ExportView
class StreamingBuffer:
    def write(self, value): return value

# FileDownloadView download file in object model File
class FileDownloadView(BaseView, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        fil = get_object_or_404(self.model, uid=kwargs['uid'])
        return fil.file_url

# FilePDFView open a pdf file in a viewer
class FilePDFView(DetailView):
    pass

# ExportView download a csv file
class ExportView(ListView):
    protect_limit = None

    def iter_items(self, items, pseudo_buffer):
        writer = csv.writer(pseudo_buffer)
        yield writer.writerow(self.fields)
        for item in items:
            yield writer.writerow(item)

    def get_queryset(self, queryset):
        if protect_limit is not None:
            return super().get_queryset(queryset)[0:self.protect_limit]
        return super().get_queryset(queryset)

    def render_to_response(self, context, **response_kwargs):
        frmat = self.request.GET.get('format', '')
        objects_list = self.get_queryset().values_list(*self.fields)
        response = StreamingHttpResponse(streaming_content=(self.iter_items(objects_list, StreamingBuffer())), content_type='text/csv',)
        response['Content-Disposition'] = 'attachment;filename=%s.csv' % get_valid_filename(make_searchable(self.model._meta.verbose_name))
        return response