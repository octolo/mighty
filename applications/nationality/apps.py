from django.conf import settings
from django.apps import AppConfig
import os.path

class Config:
    directory = os.path.dirname(os.path.realpath(__file__))

if hasattr(settings, 'NationalityConfig'):
    for config,configs in getattr(settings, 'NationalityConfig').items():
        if hasattr(Config, config):
            for key,value in configs.items():
                if hasattr(getattr(Config, config), key):
                    setattr(getattr(Config, config), key, value)


class NationalityConfig(AppConfig, Config):
    name = 'mighty.applications.nationality'
