from django.core.files import File
from django.conf import settings
from mighty.management import CSVModelCommand
from mighty.models import Nationality
from mighty.applications.nationality.apps import NationalityConfig as conf
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
import os.path

class Command(CSVModelCommand):
    fields = { 'country': 'Country', 'alpha2': 'Alpha2', 'alpha3': 'Alpha3', 'numeric': 'Numeric', 'numbering': 'Numbering' }
    number_total = 0

    def get_current_info(self):
        return self.current_object if self.ftotal == "total" else self.current_row["country"]

    def on_row(self, row):
        obj, create = Nationality.objects.get_or_create(country=row['country'])
        for field in ("alpha2", "alpha3", "numeric", "numbering"):
            if row[field]:
                setattr(obj, field, row[field])
        img = '%s/flags/%s.png' % (conf.directory, obj.alpha2.lower())
        if obj.image and os.path.isfile(obj.image.path):
            os.remove(obj.image.path)
            obj.image = None
        if os.path.isfile(img):
            f = open(img, "rb")
            flag = File(f)
            obj.image.save(img, flag, save=True)
        obj.save()
        if self.position >= 2:
            self.stop_loop = True

    def before_job(self):
        self.logger.info('Import nationalities')

    def after_job(self, *args, **kwargs):
        if not self.stop_loop:
            self.logger.info('Import phone number')
            qs = []
            for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.items():
                for value in values:
                    qs.append({"alpha": value, "numbering": prefix})
            self.ftotal = "total"
            self.each_objects(qs)

    def on_object(self, obj):
        try:
            nat = Nationality.objects.get(alpha2__iexact=obj["alpha"])
            nat.numbering = obj["numbering"]
            nat.save()
        except Nationality.DoesNotExist:
            self.errors.append(obj)
            self.logger.warning("Nationality not found: "+str(obj))
