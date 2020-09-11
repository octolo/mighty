
from django.core import serializers
from django.http import JsonResponse
from mighty.views import DetailView
from mighty.models import TranslateDict
from mighty.applications.nationality.apps import NationalityConfig as conf
from django.db.models import Q

class DictDetailView(DetailView):
    model = TranslateDict

    def get_object(self, queryset=None):
        name = self.kwargs.get('name')
        lng = self.kwargs.get('language')
        first = Q(precision__icontains=lng) | Q(search__icontains=lng) | Q(language__alpha2__icontains=lng)
        second = Q(precision__icontains=conf.default) | Q(search__icontains=conf.default) | Q(language__alpha2__icontains=conf.default)
        try:
            return TranslateDict.objects.get(first)
        except TranslateDict.DoesNotExist:
            return TranslateDict.objects.get(second)

    def render_to_response(self, context):
        trans = context['object'].translates
        key = self.request.GET.get('key', False)
        return JsonResponse({key: trans[key]} if key in trans else trans)
