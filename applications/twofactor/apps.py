from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    groups_onsave = []
    mail_protect_spam = 5
    sms_protect_spam = 5
    minutes_allowed = 5
    code_size = 6
    email_code = 'twofactor/email_code.html'
    email_template = None

    class method:
        email = True
        sms = True
        basic = False

if hasattr(settings, 'TWOFACTOR'): over_config(Config, settings.TWOFACTOR)
class TwofactorConfig(AppConfig, Config):
    name = 'mighty.applications.twofactor'
