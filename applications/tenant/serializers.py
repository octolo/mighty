from rest_framework.serializers import ModelSerializer, SlugRelatedField

from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.apps import TenantConfig as conf

TenantModel = get_tenant_model()
TenantGroup = get_tenant_model(conf.ForeignKey.group)
RoleModel = get_tenant_model(conf.ForeignKey.role)


class RoleSerializer(ModelSerializer):
    group = SlugRelatedField(
        slug_field='uid', queryset=TenantGroup.objects.all()
    )

    class Meta:
        model = RoleModel
        fields = ('uid', 'name', 'group', 'image_url', 'number')


class TenantSerializer(ModelSerializer):
    group = SlugRelatedField(
        slug_field='uid', queryset=TenantGroup.objects.all()
    )
    roles = RoleSerializer(many=True)

    class Meta:
        model = TenantModel
        fields = (
            'uid',
            'fullname',
            'str_group',
            'uid_group',
            'roles',
            'sync',
            'group',
        )
