from django.http import HttpResponse
from django.views import View

from mighty.functions import setting
from mighty.views.base import BaseView  # noqa
from mighty.views.check import CheckData, CheckSynchro  # noqa
from mighty.views.config import Config, ConfigDetailView, ConfigListView  # noqa
from mighty.views.crud import (  # noqa
    AddView,
    ChangeView,
    DeleteView,
    DetailView,
    DisableView,
    EnableView,
    ListView,
)
from mighty.views.form import FormDescView, FormView, SearchFormDesc  # noqa
from mighty.views.foxid import FoxidView  # noqa
from mighty.views.json import JsonView  # noqa
from mighty.views.model import ModelView  # noqa
from mighty.views.template import TemplateView  # noqa
from mighty.views.widget import Widget  # noqa


# Generic response
class GenericSuccess(View):
    def get(self, request):
        return HttpResponse('OK')


if 'rest_framework' in setting('INSTALLED_APPS'):
    from mighty.views.viewset import ModelViewSet as ModelViewSet
