from rest_framework.serializers import ModelSerializer
from mighty.models import Nationality
from mighty.applications.nationality import fields

class NationalitySerializer(ModelSerializer):
    class Meta:
        model = Nationality
        fields = fields.nationality