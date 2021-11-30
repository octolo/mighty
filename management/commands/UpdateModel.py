from mighty.management import ModelBaseCommand

class Command(ModelBaseCommand):
    def on_object(self, obj):
        self.current_info = obj.pk
        print(obj.pk)
        obj.save()