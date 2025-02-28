from mighty.applications.address import fields, get_address_backend
from mighty.management import ModelBaseCommand

address_backend = get_address_backend()


class Command(ModelBaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--address')
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.address = options.get('address')
        super().handle(*args, **options)

    def on_object(self, obj):
        addr_list = address_backend.give_list(self.address)
        if len(addr_list):
            addr = addr_list[0]
            data = {field: addr[field] for field in fields}
            if self.fkmodel:
                getattr(obj, self.fkmodel).update_or_create(
                    addr_backend_id=data['addr_backend_id'], defaults=data
                )
