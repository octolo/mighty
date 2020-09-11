from mighty.management import ModelBaseCommand

class Command(ModelBaseCommand):
    def on_object(self, obj):
        obj.save()