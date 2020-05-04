from rest_framework.serializers import ModelSerializer
from mighty.models.applications.nationality import Nationality
from mighty.applications.nationality import fields

class NationalitySerializer(ModelSerializer):
    class Meta:
        model = Nationality
        fields = fields.serializer