from django.views.generic.base import RedirectView

from mighty.filegenerator import FileGenerator
from mighty.views.base import BaseView
from mighty.views.crud import DetailView, ListView

# Buffer for ExportView


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
    fields = ()

    def get_queryset(self, queryset):
        qs = super().get_queryset(queryset)
        return qs[0 : self.protect_limit] if protect_limit is not None else qs

    def render_to_response(self, context, **response_kwargs):
        fileResponse = FileGenerator(
            fields=self.fields,
            filename=self.model.meta_.verbose_name,
            items=self.get_queryset().values_list(*self.fields),
        )
        return fileResponse.get_by_format(self.request.GET.get('format', 'csv'))
