from django.conf import settings
from rest_framework.serializers import ModelSerializer

from mighty.models import User, Email, Phone, InternetProtocol
from mighty.applications.user import fields
from mighty.applications.nationality import serializers as nationality_serializers

class EmailSerializer(ModelSerializer):
    class Meta:
        models = Email
        fields = ('email', 'default')

class PhoneSerializer(ModelSerializer):
    class Meta:
        models = Phone
        fields = ('phone', 'default')

class InternetProtocolSerializer(ModelSerializer):
    class Meta:
        models = InternetProtocol
        fields = ('ip', 'default')

class UserSerializer(ModelSerializer):
    user_email = EmailSerializer(many=True)
    user_phone = PhoneSerializer(many=True)
    user_ip = InternetProtocolSerializer(many=True)

    class Meta:
        model = User
        fields = fields.serializer

if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    class UserSerializer(UserSerializer):
        nationalities = nationality_serializers.NationalitySerializer(many=True)