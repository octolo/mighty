from django.core.validators import EmailValidator, ValidationError

from mighty.applications.user import get_user_email_model
from mighty.functions import make_searchable
from mighty.models import UserPhone
from mighty.views import CheckData

UserEmailModel = get_user_email_model()


class UserEmailCheckView(CheckData):
    permission_classes = ()
    model = UserEmailModel
    test_field = 'email'

    def get_data(self):
        return make_searchable(self.request.GET.get('check').lower())

    def check_data(self):
        validator = EmailValidator()
        try:
            validator(self.get_data())
            return super().check_data()
        except ValidationError as e:
            return {'code': '002', 'error': str(e.message)}


class UserPhoneCheckView(CheckData):
    permission_classes = ()
    model = UserPhone
    test_field = 'phone'

    def check_data(self):
        try:
            phone = '+' + self.request.GET.get('check')
            validate_international_phonenumber(phone)
            return super().check_data()
        except ValidationError as e:
            return {'code': '002', 'error': str(e.message)}
