from django.apps import AppConfig
from django.conf import settings

class Config:
    methods = ['email', 'sms', 'basic']
    methods_ws = ['email', 'sms']

    class method:
        email = True
        sms = True
        basic = True

if hasattr(settings, 'TWOFACTOR'):
    for config,configs in getattr(settings, 'TWOFACTOR').items():
        if hasattr(Config, config):
            for key,value in configs.items():
                if hasattr(getattr(Config, config), key):
                    setattr(getattr(Config, config), key, value)

class TwofactorConfig(AppConfig, Config):
    name = 'mighty.applications.twofactor'
