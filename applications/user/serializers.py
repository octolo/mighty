from django.conf import settings
from rest_framework.serializers import ModelSerializer
from mighty.models import User, UserEmail, UserPhone, InternetProtocol
from mighty.applications.user import fields
from mighty.applications.nationality import serializers as nationality_serializers
from mighty.applications.user import get_form_fields

allfields = get_form_fields()
required = get_form_fields('required')
optional = get_form_fields('optional')

class UserEmailSerializer(ModelSerializer):
    class Meta:
        models = UserEmail
        fields = ('email', 'default')

class UserPhoneSerializer(ModelSerializer):
    class Meta:
        models = UserPhone
        fields = ('phone', 'default')

class InternetProtocolSerializer(ModelSerializer):
    class Meta:
        models = InternetProtocol
        fields = ('ip', 'default')

class UserSerializer(ModelSerializer):
    user_email = UserEmailSerializer(many=True)
    user_phone = UserPhoneSerializer(many=True)

    class Meta:
        model = User
        fields = fields.serializer

if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    class UserSerializer(UserSerializer):
        nationalities = nationality_serializers.NationalitySerializer(many=True)

class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = allfields