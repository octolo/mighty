from rest_framework.serializers import ModelSerializer

from mighty.applications.nationality import fields
from mighty.models import Nationality


class NationalitySerializer(ModelSerializer):
    class Meta:
        model = Nationality
        fields = fields.nationality
