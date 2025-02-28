from mighty.applications.address import fields
from mighty.management import ModelBaseCommand


class AddressCommand(ModelBaseCommand):
    address_fields = fields

    def add_arguments(self, parser):
        super().add_arguments(parser)
        for field in fields:
            parser.add_argument('--%s' % field, default=None)

    def handle(self, *args, **options):
        for field in fields:
            setattr(self, field, options.get(field))
        super().handle(*args, **options)

    @property
    def has_address(self):
        for field in fields:
            if getattr(self, field):
                return True
        return False
