from django.apps import AppConfig
from django.conf import settings

class Config:
    pass

if hasattr(settings, 'LOGGER'):
    for config,configs in getattr(settings, 'LOGGER').items():
        if hasattr(Config, config):
            for key,value in configs.items():
                if hasattr(getattr(Config, config), key):
                    setattr(getattr(Config, config), key, value)

class LoggerConfig(AppConfig, Config):
    name = 'mighty.applications.logger'
