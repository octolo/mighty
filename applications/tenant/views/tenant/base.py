from django.shortcuts import get_object_or_404
from mighty.functions import get_descendant_value
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.serializers import TenantSerializer

TenantModel = get_tenant_model(TenantConfig.ForeignKey.tenant)

class TenantBase:
    serializer_class = TenantSerializer
    model = TenantModel
    queryset = TenantModel.objectsB.all()
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_object(self):
        args = {
            "user": self.request.user,
            "uid": self.kwargs.get('uid', None),
        }
        return get_object_or_404(self.model, **args)

    def get_queryset(self, queryset=None):
        return self.queryset.filter(user=self.request.user)

    def get_fields(self, tenant):
        return {
            "uid": tenant.uid,
            "status": tenant.status,
            "company_representative": tenant.company_representative,
            "sync": tenant.sync,
            "group": {key: str(get_descendant_value(path, tenant)) 
                for key,path in TenantConfig.group_api.items() 
                    if get_descendant_value(path, tenant)},
            "roles": [{'uid': role.uid, 'name': role.name} for role in tenant.roles.all()]
        }

    def get_tenants(self):
        return [self.get_fields(tenant) for tenant in self.get_queryset()]