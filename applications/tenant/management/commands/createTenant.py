from mighty.applications.tenant import get_tenant_model
from mighty.applications.tenant.apps import TenantConfig
from mighty.management import CSVModelCommand

TenantModel = get_tenant_model(TenantConfig.ForeignKey.tenant)
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)
RoleModel = get_tenant_model(TenantConfig.ForeignKey.role)


class Command(CSVModelCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--role')
        parser.add_argument('--tenant')
        parser.add_argument('--group')
        parser.add_argument('--groupfield', default='id')

    def handle(self, *args, **options):
        self.role = options.get('role').split(self.splitter)
        self.tenant = options.get('tenant')
        self.group = options.get('group')
        self.groupfield = options.get('groupfield')
        self.group = TenantModel.group.get_queryset().get(**{self.groupfield: self.group})
        super().handle(*args, **options)

    def add_role(self, tenant):
        roles = RoleModel.objects.filter(group=self.group, name__in=self.role)
        if len(roles):
            tenant.roles.add(*roles)

    def do(self):
        if self.csvfile:
            self.loop_qs('on_row')
        else:
            self.create_tenant(self.tenant)

    def on_row(self, row):
        self.create_tenant(row['email'])

    def create_tenant(self, tenant):
        user = self.get_user(tenant)
        tenant, create = TenantModel.objects.get_or_create(user=user, group=self.group)
        self.add_role(tenant)
