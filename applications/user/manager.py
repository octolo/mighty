from django.contrib.auth.models import UserManager
from mighty.applications.user import username_generator_v2, choices

#FIXME: Need unique method to create user

PrefetchRelated = ('user_email', 'user_phone', 'user_ip', 'user_useragent')
class UserManager(UserManager):
    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        if username is None: username = username_generator_v2(email)
        extra_fields.setdefault('method', choices.METHOD_CREATESU)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('create_by', '0.system')
        extra_fields.setdefault('update_by', '0.system')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, email, password, **extra_fields)

    def get_queryset(self):
        return super().get_queryset().prefetch_related(*PrefetchRelated)
