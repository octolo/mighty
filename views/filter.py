from django.http import JsonResponse

from mighty.descriptors.filter import FilterDescriptor
from mighty.views.template import TemplateView

class FilterDescView(TemplateView):
    descriptor_class = FilterDescriptor
    filters = []

    def get_context_data(self, **kwargs):
        return self.descriptor_class(self.filters).as_json()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)