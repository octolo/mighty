from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from mighty.applications.user import translates as _
from mighty.functions import get_model

def validate_phone(value, exclude):
    if value:
        UserModel = get_user_model()
        fltr = Q(phone=value)|Q(user_phone__phone=value)
        if UserModel.objects.exclude(**exclude).filter(fltr).exists():
            raise ValidationError(_.error_phone_already)

def validate_email(value):
    if value:
        UserModel = get_user_model()
        fltr = Q(email=value)|Q(user_email__email=value)
        try:
            UserModel.objects.get(fltr)
            raise ValidationError(_.error_email_already)
        except UserModel.DoesNotExist:
            pass

def validate_trashmail(value):
    domain = value.split("@")[1]
    if get_model("mighty", "Trashmail").objects.filter(domain=domain).count():
        raise ValidationError("This is trashmail")