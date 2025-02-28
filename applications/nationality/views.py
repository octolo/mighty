from django.db.models import Q
from django.http import JsonResponse

from mighty.applications.nationality.apps import NationalityConfig as conf
from mighty.models import Nationality, TranslateDict, Translator
from mighty.views import DetailView, ListView


class DictListView(ListView):
    model = TranslateDict

    def get_queryset(self, queryset=None):
        lng = self.request.GET.get('lang', conf.default)
        lng = lng if lng in conf.availables else conf.default
        first = (
            Q(precision__icontains=lng)
            | Q(search__icontains=lng)
            | Q(language__alpha2__icontains=lng)
        )
        second = (
            Q(precision__icontains=conf.default)
            | Q(search__icontains=conf.default)
            | Q(language__alpha2__icontains=conf.default)
        )
        try:
            return TranslateDict.objectsB.filter(first)
        except TranslateDict.DoesNotExist:
            return TranslateDict.objectsB.filter(second)

    def render_to_response(self, context):
        return JsonResponse({
            tr.translator.name: tr.translates for tr in context['object_list']
        })


class DictDetailView(DetailView):
    model = TranslateDict

    def get_object(self, queryset=None):
        name = self.kwargs.get('name')
        lng = self.request.GET.get('lang', conf.default)
        lng = lng if lng in conf.availables else conf.default
        first = (
            Q(precision__icontains=lng)
            | Q(search__icontains=lng)
            | Q(language__alpha2__icontains=lng)
        )
        second = (
            Q(precision__icontains=conf.default)
            | Q(search__icontains=conf.default)
            | Q(language__alpha2__icontains=conf.default)
        )
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


class TrLoad(CreateAPIView):
    queryset = Translator.objects.all()
    authentication_classes = []  # disables authentication
    permission_classes = []

    def post(self, request, format=None):
        path = request.data.get('path')
        trans = request.data.get('trans')
        path = path.split('.')
        default_nationality = Nationality.objects.get(
            alpha2__iexact=conf.default
        )
        translator, created1 = Translator.objects.get_or_create(name=path[0])
        translatedict, created2 = TranslateDict.objects.get_or_create(
            translator=translator, language=default_nationality
        )
        len(path) - 1
        if not translatedict.translates:
            translatedict.translates = {}
        if len(path) == 3:
            if path[1] in translatedict.translates:
                translatedict.translates[path[1]][path[2]] = trans
            else:
                translatedict.translates[path[1]] = {path[2]: trans}
        elif len(path) == 4:
            if path[1] in translatedict.translates:
                if path[2] in translatedict.translates[path[1]]:
                    translatedict.translates[path[1]][path[2]][path[3]] = trans
                else:
                    translatedict.translates[path[1]][path[2]] = {
                        path[3]: trans
                    }
            else:
                translatedict.translates[path[1]] = {path[2]: {path[3]: trans}}
        else:
            translatedict.translates[path[1]] = trans

        translatedict.save()
        return Response({'translator': created1, 'translatedict': created2})
