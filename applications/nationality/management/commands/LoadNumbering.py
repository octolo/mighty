from mighty.management import ModelBaseCommand
from mighty.models import Nationality


class Command(ModelBaseCommand):
    def get_queryset(self, *args, **kwargs):
        from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE

        qs = []
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.items():
            qs.extend({'alpha': value, 'numbering': prefix} for value in values)
        return qs

    def on_object(self, obj):
        try:
            nat = Nationality.objects.get(alpha2__iexact=obj['alpha'])
            nat.numbering = obj['numbering']
            nat.save()
        except Nationality.DoesNotExist:
            self.errors.append(obj)
