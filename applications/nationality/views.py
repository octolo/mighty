
from mighty.views.viewsets import ModelViewSet, ApiModelViewSet
from mighty.models import Nationality
from mighty.applications.nationality import serializers, filters


class NationalityViewSet(ModelViewSet):
    list_is_ajax = True
    model = Nationality
    slug = '<int:pk>'
    slug_field = "pk"
    slug_url_kwarg = "pk"

class NationalityApiViewSet(ApiModelViewSet):
    model = Nationality
    slug = '<int:pk>'
    slug_field = "pk"
    slug_url_kwarg = "pk"
    lookup_field = "pk"
    serializer_class = serializers.NationalitySerializer
    filter_model = filters.NationalityFilter