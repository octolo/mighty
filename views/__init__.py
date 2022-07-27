
from django.views import View
from django.http import HttpResponse
from mighty.functions import setting
from mighty.views.base import BaseView
from mighty.views.template import TemplateView
from mighty.views.model import ModelView
from mighty.views.crud import ListView, DetailView, ChangeView, DeleteView, AddView, EnableView, DisableView
from mighty.views.form import FormView, FormDescView, SearchFormDesc
from mighty.views.file import FileDownloadView, FilePDFView, ExportView
from mighty.views.pdf import PDFView
from mighty.views.config import Config, ConfigListView, ConfigDetailView
from mighty.views.check import CheckData, CheckSynchro
from mighty.views.widget import Widget
from mighty.views.foxid import FoxidView
from mighty.views.json import JsonView

# Generic response
class GenericSuccess(View):
    def get(self, request):
        return HttpResponse('OK')

if 'rest_framework' in setting('INSTALLED_APPS'):
    from mighty.views.viewset import ModelViewSet
