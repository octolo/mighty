from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model

from mighty import over_config
from mighty.functions import setting


class Config:
    count_related = "roles_tenant"
    ordering = ("id",)
    search_filter = {}
    tenant_user_related = None
    tenant_roles_related = None
    tenant_group_related = None
    roles = [
        {
            'name': 'manager',
            'is_immutable': True,
        },
        {
            'name': 'user',
            'is_immutable': True,
        },
        {
            'name': 'comptable',
        },
        {
            'name': 'ressources humaines',
        },
        {
            'name': 'avocat',
        },
        {
            'name': 'juriste',
        },
        {
            'name': 'salarié',
        },
    ]
    group_api = {
        "uid": "group.uid",
        "image_url": "group.image_url",
        "since": "group.since",
    }

    class ForeignKey:
        group = setting('TENANT_GROUP', 'auth.Group')
        role = setting('TENANT_ROLE', 'mighty.Role')
        tenant = setting('TENANT_MODEL', 'mighty.Tenant')
        missive = setting('TENANT_MISSIVE', 'mighty.Missive')
        nationalities = setting('TENANT_NATIONALITY', 'mighty.Nationality')
        user = settings.AUTH_USER_MODEL
        optional = False

if hasattr(settings, 'TENANT'): over_config(Config, settings.TENANT)
class TenantConfig(AppConfig, Config):
    name = 'mighty.applications.tenant'

    def ready(self):
        from . import signals
