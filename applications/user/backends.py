from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

has_authenticate_app = True if 'mighty.applications.twofactor' in settings.INSTALLED_APPS else False
if has_authenticate_app:
    from mighty.applications.twofactor.apps import TwofactorConfig

UserModel = get_user_model()
class AuthBasicBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            if has_authenticate_app and 'method' in kwargs and kwargs['method'] =='basic' and TwofactorConfig.method.basic:
                user = UserModel.objects.get(uid=username)
            else:
                user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                if hasattr(request, 'META'):
                    user.get_client_ip(request)
                    user.get_user_agent(request)
                return user