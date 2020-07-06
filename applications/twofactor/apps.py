from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    site = None
    sender_name = None
    sender_email = None
    reply_name = None
    reply_email = None
    groups_onsave = []

    class method:
        email = True
        sms = True
        basic = True

if hasattr(settings, 'TWOFACTOR'): over_config(Config, settings.TWOFACTOR)
class TwofactorConfig(AppConfig, Config):
    name = 'mighty.applications.twofactor'
