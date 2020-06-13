from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    delimiter = '__'

if hasattr(settings, 'CHAT'): over_config(Config, getattr(settings, 'CHAT'))
class ChatConfig(AppConfig, Config):
    name = 'mighty.applications.chat'
