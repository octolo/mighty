from django.http import JsonResponse
from django.views.generic.edit import FormView

from mighty.descriptors.form import FormDescriptor
from mighty.forms import SearchForm
from mighty.views.base import BaseView
from mighty.views.template import TemplateView


class FormView(BaseView, FormView):
    pass


class FormConfigView(FormView):
    pass


class FormDescView(TemplateView):
    descriptor_class = FormDescriptor
    form = None

    def get_context_data(self, **kwargs):
        return FormDescriptor(self.form, self.request, **self.kwargs).as_json()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs, safe=False)


class SearchFormDesc(FormDescView):
    form = SearchForm
