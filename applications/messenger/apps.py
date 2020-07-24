from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    sender_name = None
    sender_email = None
    reply_name = None
    reply_email = None
    user_or_invitation = 'mighty.UserOrInvitation'
    missive = 'mighty.Missive'
    delimiter = '__'
    limit_choices_to = {'app_label': 'mighty', 'model__in': ['user', 'userorinvitation']}
    missive_backends = settings.MISSIVE_BACKENDS if hasattr(settings, 'MISSIVE_BACKENDS') else ['mighty.applications.messenger.backend']

if hasattr(settings, 'MESSENGER'): over_config(Config, getattr(settings, 'MESSENGER'))
class MessengerConfig(AppConfig, Config):
    name = 'mighty.applications.messenger'
