from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    user_or_inivitation_lct = {'app_label': 'mighty', 'model__in': ['user', 'userorinvitation']}
    invitation_enable = True
    invitation_days = 7
    invitation_url = 'http://%(domain)s/user/invitation/%(uid)s/?token=%(token)s'

    class ForeignKey:
        missive = 'mighty.Missive'
        user = settings.AUTH_USER_MODEL
        nationalities = 'mighty.Nationality'
        optional = False

    class Field:
        username = 'email'
        required = ()
        style = ['dark', 'light']

if hasattr(settings, 'USER'): over_config(Config, settings.USER)
class UserConfig(AppConfig, Config):
    name = 'mighty.applications.user'

    def ready(self):
        from . import signals