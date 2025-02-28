from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class AuthBasicBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        field_type = kwargs.get('field_type')
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None
        try:
            if field_type == 'uid' and hasattr(UserModel, 'uid'):
                user = UserModel.objects.get(uid=username)
            else:
                user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(
                user
            ):
                if hasattr(request, 'META'):
                    user.get_client_ip(request)
                    user.get_user_agent(request)
                return user
