from django.conf import settings
from rest_framework.serializers import ModelSerializer, ValidationError

from mighty.applications.nationality import (
    serializers as nationality_serializers,
)
from mighty.applications.user import (
    fields,
    get_form_fields,
    get_user_email_model,
)
from mighty.applications.user.apps import UserConfig
from mighty.models import InternetProtocol, User, UserPhone

allfields = get_form_fields()
required = get_form_fields('required')
optional = get_form_fields('optional')

UserEmailModel = get_user_email_model()


class UserEmailSerializer(ModelSerializer):
    class Meta:
        models = UserEmailModel
        fields = ('email', ) + (UserConfig.ForeignKey.email_field, )


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

    def validate_cgu(self, value):
        if not value:
            raise ValidationError('Validation error')
        return value
