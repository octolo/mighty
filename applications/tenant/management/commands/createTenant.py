from mighty.management import ModelBaseCommand
from mighty.applications.tenant import get_tenant_model

Tenant = get_tenant_model()

class Command(ModelBaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--tenant")
        parser.add_argument("--group")
        parser.add_argument("--groupfield", default="id")

    def handle(self, *args, **options):
        self.tenant = options.get("tenant")
        self.group = options.get("group")
        self.groupfield = options.get("groupfield")
        super(ModelBaseCommand, self).handle(*args, **options)

    def do(self):
        user = self.get_user(self.tenant)
        group = Tenant.group.get_queryset().get(**{self.groupfield: self.group})
        tenant, create = Tenant.objects.get_or_create(user=user, group=group)
