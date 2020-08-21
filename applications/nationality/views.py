
from django.core import serializers
from django.http import JsonResponse
from mighty.views import DetailView
from mighty.models import TranslateDict

class DictDetailView(DetailView):
    model = TranslateDict

    def get_object(self, queryset=None):
        return TranslateDict.objects.get(translator__name=self.kwargs.get('name'), language__alpha2__iexact=self.kwargs.get('language'))

    def render_to_response(self, context):
        trans = context['object'].translates
        key = self.request.GET.get('key', False)
        return JsonResponse({key: trans[key]} if key in trans else trans)

#class NationalityViewSet(ModelViewSet):
#    model = Nationality
#    slug = '<uuid:uid>'
#    slug_field = "uid"
#    slug_url_kwarg = "uid"
#
#if 'rest_framework' in settings.INSTALLED_APPS:
#    from mighty.views.viewsets import ApiModelViewSet
#    from mighty.applications.nationality import serializers
#    class NationalityApiViewSet(ApiModelViewSet):
#        model = Nationality
#        slug = '<int:pk>'
#        slug_field = "pk"
#        slug_url_kwarg = "pk"
#        lookup_field = "pk"
#        serializer_class = serializers.NationalitySerializer
#        # filter_model = filters.NationalityFilter
#        queryset = Nationality.objects.all()