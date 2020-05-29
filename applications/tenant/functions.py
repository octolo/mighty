from django.conf import settings
from django.utils.module_loading import import_string

def get_tenant_model():
    return settings.TENANT_MODEL

def get_tenant_model():
    return settings.TENANT_USER