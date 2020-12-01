from django.conf import settings
from rest_framework.serializers import ModelSerializer
from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.apps import TenantConfig as conf

TenantModel = get_tenant_model()

class TenantSerializer(ModelSerializer):
    class Meta:
        model = TenantModel
        fields = ('uid', 'fullname', 'str_group', 'uid_group')