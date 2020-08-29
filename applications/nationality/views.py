
from django.core import serializers
from django.http import JsonResponse
from mighty.views import DetailView
from mighty.models import TranslateDict
from mighty.applications.nationality.apps import NationalityConfig as conf

class DictDetailView(DetailView):
    model = TranslateDict

    def get_object(self, queryset=None):
        try:
            return TranslateDict.objects.get(translator__name=self.kwargs.get('name'), search__icontains=self.kwargs.get('language'))
        except TranslateDict.DoesNotExist:
            return TranslateDict.objects.get(translator__name=self.kwargs.get('name'), search__icontains=conf.default)

    def render_to_response(self, context):
        trans = context['object'].translates
        key = self.request.GET.get('key', False)
        return JsonResponse({key: trans[key]} if key in trans else trans)
