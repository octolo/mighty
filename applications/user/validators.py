from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from mighty.applications.user import translates as _

def validate_phone(value):
    UserModel = get_user_model()
    fltr = Q(phone=value)|Q(user_phone__phone=value)
    if value:
        try:
            UserModel.objects.get(fltr)
            raise ValidationError(_.error_phone_already)
        except UserModel.DoesNotExist:
            pass

def validate_email(value):
    UserModel = get_user_model()
    fltr = Q(phone=value)|Q(user_email__email=value)
    if value:
        try:
            UserModel.objects.get(fltr)
            raise ValidationError(_.error_email_already)
        except UserModel.DoesNotExist:
            pass