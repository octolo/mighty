from django.conf import settings
from rest_framework.serializers import ModelSerializer
from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.apps import TenantConfig as conf

TenantModel = get_tenant_model()
RoleModel = get_tenant_model(conf.ForeignKey.role)

class RoleSerializer(ModelSerializer):
    class Meta:
        model = RoleModel
        fields = ('uid', 'name')

class TenantSerializer(ModelSerializer):
    roles = RoleSerializer(many=True)

    class Meta:
        model = TenantModel
        fields = ('uid', 'fullname', 'str_group', 'uid_group', 'roles', 'sync')