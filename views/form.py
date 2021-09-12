from django.views.generic.edit import FormView
from django.http import JsonResponse

from mighty.descriptors.form import FormDescriptor
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
        return self.descriptor_class(self.form()).as_json()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)