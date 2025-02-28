from rest_framework.serializers import ModelSerializer

from mighty.applications.address import fields


class AddressSerializer(ModelSerializer):
    class Meta:
        fields = fields
