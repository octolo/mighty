from django.apps import AppConfig
from django.conf import settings

class Config:
    class Field:
        username = 'email'
        required = ('username', 'phone')

if hasattr(settings, 'UserConfig'):
    for config,configs in getattr(settings, 'UserConfig').items():
        if hasattr(Config, config):
            for key,value in configs.items():
                if hasattr(getattr(Config, config), key):
                    setattr(getattr(Config, config), key, value)

class UserConfig(AppConfig, Config):
    name = 'mighty.applications.user'

    def ready(self):
        from . import signals