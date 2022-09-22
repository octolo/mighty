from mighty.management import ModelBaseCommand
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model

TenantModel = get_tenant_model(TenantConfig.ForeignKey.tenant)
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)
RoleModel = get_tenant_model(TenantConfig.ForeignKey.role)

class Command(ModelBaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--role")
        parser.add_argument("--tenant")
        parser.add_argument("--group")
        parser.add_argument("--groupfield", default="id")

    def handle(self, *args, **options):
        self.role = options.get("role").split(self.splitter)
        self.tenant = options.get("tenant")
        self.group = options.get("group")
        self.groupfield = options.get("groupfield")
        self.group = TenantModel.group.get_queryset().get(**{self.groupfield: self.group})
        super(ModelBaseCommand, self).handle(*args, **options)

    def add_role(self, tenant):
        roles = RoleModel.objects.filter(group=self.group, name__in=self.role)
        if len(roles):
            tenant.roles.add(*roles)

    def do(self):
        user = self.get_user(self.tenant)
        tenant, create = TenantModel.objects.get_or_create(user=user, group=self.group)
        self.add_role(tenant)
