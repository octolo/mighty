default_app_config = 'mighty.applications.tenant.apps.TenantConfig'

from django.apps import apps as django_apps
from mighty.applications.tenant.apps import TenantConfig as conf

def get_tenant_model(model=conf.ForeignKey.tenant):
    tenant = model.split('.')
    return django_apps.get_model(tenant[0], tenant[1])