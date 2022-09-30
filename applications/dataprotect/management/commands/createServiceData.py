from mighty.management import ModelBaseCommand
from mighty.models import ServiceData
from mighty.applications.dataprotect import fields

class Command(ModelBaseCommand):
    string_arguments = fields.servicedata

    def do(self):
        data = {field: getattr(self, field) for field in fields.servicedata}
        ServiceData.objects.get_or_create(**data)
