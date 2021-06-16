from django.conf import settings
from mighty.management import ModelBaseCommand
from mighty.models import Nationality
from mighty.applications.nationality.apps import NationalityConfig as conf
import os.path

class Command(ModelBaseCommand):

    def get_queryset(self, *args, **kwargs):
        from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
        qs = []
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.items():
            for value in values:
                qs.append({"alpha": value, "numbering": prefix})
        return qs

    def on_object(self, obj):
        try:
            nat = Nationality.objects.get(alpha2__iexact=obj["alpha"])
            nat.numbering = obj["numbering"]
            nat.save()
        except Nationality.DoesNotExist:
            self.errors.append(obj)
        