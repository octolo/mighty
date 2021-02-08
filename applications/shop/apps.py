from django.apps import AppConfig
from django.conf import settings
from mighty import over_config

class Config:
    pass

if hasattr(settings, 'SHOP'): over_config(Config, settings.SHOP)
class ShopConfig(AppConfig, Config):
    name = 'shop'
