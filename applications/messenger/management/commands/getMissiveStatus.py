from django.conf import settings
from mighty.management import ModelBaseCommand
from mighty.models import Missive

class Command(ModelBaseCommand):
    model = Missive

    def on_object(self, obj):
        obj.check_status()