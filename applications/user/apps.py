from django.apps import AppConfig
from django.conf import settings
from mighty.functions import over_config

class Config:
    test = 'toto'
    class Field:
        username = 'email'
        required = ()

#if hasattr(settings, 'USER'):
#    for config,configs in getattr(settings, 'USER').items():
#        if hasattr(Config, config):
#            for key,value in configs.items():
#                if hasattr(getattr(Config, config), key):
#                    setattr(getattr(Config, config), key, value)

if hasattr(settings, 'USER'):
    over_config(Config, settings.USER)
class UserConfig(AppConfig, Config):
    name = 'mighty.applications.user'

    def ready(self):
        from . import signals