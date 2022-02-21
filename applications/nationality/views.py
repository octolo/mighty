
from django.core import serializers
from django.http import JsonResponse
from mighty.views import DetailView, ListView
from mighty.models import Nationality, TranslateDict, Translator
from mighty.applications.nationality.apps import NationalityConfig as conf
from django.db.models import Q


class DictListView(ListView):
    model = TranslateDict

    def get_queryset(self, queryset=None):
        lng = self.request.GET.get('lang', conf.default)
        lng = lng if lng in conf.availables else conf.default
        first = Q(precision__icontains=lng) | Q(search__icontains=lng) | Q(language__alpha2__icontains=lng)
        second = Q(precision__icontains=conf.default) | Q(search__icontains=conf.default) | Q(language__alpha2__icontains=conf.default)
        try:
            return TranslateDict.objectsB.filter(first)
        except TranslateDict.DoesNotExist:
            return TranslateDict.objectsB.filter(second)

    def render_to_response(self, context):
        return JsonResponse({tr.translator.name: tr.translates for tr in context['object_list']})

class DictDetailView(DetailView):
    model = TranslateDict

    def get_object(self, queryset=None):
        name = self.kwargs.get('name')
        lng = self.request.GET.get('lang', conf.default)
        lng = lng if lng in conf.availables else conf.default
        first = Q(precision__icontains=lng) | Q(search__icontains=lng) | Q(language__alpha2__icontains=lng)
        second = Q(precision__icontains=conf.default) | Q(search__icontains=conf.default) | Q(language__alpha2__icontains=conf.default)
        try:
            return TranslateDict.objects.get(Q(name=name) & (first))
        except TranslateDict.DoesNotExist:
            return TranslateDict.objects.get(Q(name=name) & (second))

    def render_to_response(self, context):
        trans = context['object'].translates
        key = self.request.GET.get('key', False)
        return JsonResponse({key: trans[key]} if key in trans else trans)

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from mighty.applications.nationality.apps import NationalityConfig as conf

class TrLoad(CreateAPIView):
    queryset = Translator.objects.all()

    def post(self, request, format=None):
        path = request.data.get("path")
        trans = request.data.get("trans")
        path = path.split(".")
        default_nationality = Nationality.objects.get(alpha2__iexact=conf.default)
        translator, created1 = Translator.objects.get_or_create(name=path[0])
        translatedict, created2 = TranslateDict.objects.get_or_create(
            translator=translator,
            language=default_nationality
        )
        cnt = len(path)-1
        if not translatedict.translates: translatedict.translates = {}
        ntr = translatedict.translates
        pos = 0
        for p in path[1:]:
            pos+=1
            ntr[p] = trans if pos == cnt else {}
            ntr = ntr[p]
        translatedict.save()
        return Response({"translator": created1, "translatedict": created2 })