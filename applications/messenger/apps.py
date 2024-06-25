from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    sender_name = None
    sender_email = None
    reply_name = None
    reply_email = None
    missive = 'mighty.Missive'
    delimiter = '__'
    missive_backend = settings.MISSIVE_BACKEND if hasattr(settings, 'MISSIVE_BACKEND') else 'mighty.applications.messenger.backends'

    class enable:
        email = True
        sms = False
        postal = False

if hasattr(settings, 'MESSENGER'): over_config(Config, getattr(settings, 'MESSENGER'))
class MessengerConfig(AppConfig, Config):
    name = 'mighty.applications.messenger'
