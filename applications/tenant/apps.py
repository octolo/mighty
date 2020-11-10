from django.apps import AppConfig
from django.conf import settings
from mighty import over_config
from django.contrib.auth import get_user_model

class Config:
    tenant = 'mighty.Tenant'
    invitation = 'mighty.Invitation'
    invitation_url = 'http://%(domain)s/user/tenants/'

    class ForeignKey:
        group = 'auth.Group'
        role = 'mighty.Role'
        user = settings.AUTH_USER_MODEL

if hasattr(settings, 'TENANT'): over_config(Config, settings.TENANT)
class TenantConfig(AppConfig, Config):
    name = 'mighty.applications.tenant'