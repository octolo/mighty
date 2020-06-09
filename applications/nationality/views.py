
from django.conf import settings
from mighty.views.viewsets import ModelViewSet
from mighty.models import Nationality
from mighty.applications.nationality import filters

class NationalityViewSet(ModelViewSet):
    list_is_ajax = True
    model = Nationality
    slug = '<int:pk>'
    slug_field = "pk"
    slug_url_kwarg = "pk"

if 'rest_framework' in settings.INSTALLED_APPS:
    from mighty.views.viewsets import ApiModelViewSet
    from mighty.applications.nationality import serializers
    class NationalityApiViewSet(ApiModelViewSet):
        model = Nationality
        slug = '<int:pk>'
        slug_field = "pk"
        slug_url_kwarg = "pk"
        lookup_field = "pk"
        serializer_class = serializers.NationalitySerializer
        filter_model = filters.NationalityFilter