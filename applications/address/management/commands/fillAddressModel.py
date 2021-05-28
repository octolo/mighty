from mighty.management import ModelBaseCommand
from mighty.applications.address import get_address_backend, fields
address_backend = get_address_backend()

class Command(ModelBaseCommand):
    def on_object(self, obj):
        if not obj.address and obj.raw:
            try:
                addr = address_backend.give_list(obj.raw)[0]
                for field in fields:
                    setattr(obj, field, addr[field])
                obj.save()
            except Exception:
                pass
        else:
            obj.delete()
        