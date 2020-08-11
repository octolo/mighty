from django.apps import AppConfig
from django.conf import settings
from mighty import over_config
from django.contrib.auth import get_user_model

class Config:
    class ForeignKey:
        Tenant = 'auth.Group'
        Role = 'Role'

if hasattr(settings, 'TENANT'): over_config(Config, settings.TENANT)
class TenantConfig(AppConfig, Config):
    name = 'mighty.applications.tenant'