from django.apps import AppConfig

from mighty import over_config
from mighty.functions import setting


class Config:
    pass


over_config(Config, setting('DATAPROTECT'))


class DataprotectConfig(AppConfig, Config):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mighty.applications.dataprotect'
