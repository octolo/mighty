from mighty.management.commands.UpdateModel import UpdateModel

class Command(UpdateModel):
    def do_update(self, obj):
        obj.save()