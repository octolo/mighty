from django.apps import AppConfig
from django.conf import settings
from mighty import over_config
from mighty.functions import setting
from django.contrib.auth import get_user_model

class Config:
    ordering = ("id",)
    search_filter = {}
    tenant_user_related = None
    tenant_group_related = None

    group_api = {
        "uid": "group.uid",
        "image_url": "group.image_url",
    }

    class ForeignKey:
        group = setting('TENANT_GROUP', 'auth.Group')
        tenant = setting('TENANT_MODEL', 'mighty.Tenant')
        missive = setting('TENANT_MISSIVE', 'mighty.Missive')
        nationalities = setting('TENANT_NATIONALITY', 'mighty.Nationality')
        user = settings.AUTH_USER_MODEL
        optional = False

if hasattr(settings, 'TENANT'): over_config(Config, settings.TENANT)
class TenantConfig(AppConfig, Config):
    name = 'mighty.applications.tenant'
