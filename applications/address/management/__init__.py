from mighty.applications.address import fields
from mighty.management import ModelBaseCommand


class AddressCommand(ModelBaseCommand):
    address_fields = fields

    def add_arguments(self, parser):
        super().add_arguments(parser)
        for field in fields:
            parser.add_argument(f'--{field}', default=None)

    def handle(self, *args, **options):
        for field in fields:
            setattr(self, field, options.get(field))
        super().handle(*args, **options)

    @property
    def has_address(self):
        return any(getattr(self, field) for field in fields)
