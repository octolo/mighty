from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    class Field:
        username = 'email'
        required = ()
        style = ['dark', 'light']

if hasattr(settings, 'USER'): over_config(Config, settings.USER)
class UserConfig(AppConfig, Config):
    name = 'mighty.applications.user'

    def ready(self):
        from . import signals