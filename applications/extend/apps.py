from django.apps import AppConfig
from django.conf import settings

from mighty import over_config


class Config:
    pass


if hasattr(settings, 'EXTEND'):
    over_config(Config, settings.EXTEND)


class ExtendConfig(AppConfig, Config):
    name = 'mighty.applications.extend'
