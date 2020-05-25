from django.apps import AppConfig
from django.conf import settings
from mighty.functions import over_config
import os.path

class Config:
    directory = os.path.dirname(os.path.realpath(__file__))

if hasattr(settings, 'NATIONALITY'):
    over_config(Config, settings.NATIONALITY)
class NationalityConfig(AppConfig, Config):
    name = 'mighty.applications.nationality'
