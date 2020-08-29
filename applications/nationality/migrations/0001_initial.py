from django.db import migrations
from django.core.files import File
from mighty.applications.nationality.apps import NationalityConfig as conf
import os.path, csv

def load_nationalities(apps, schema_editor):
    fields = ['country', 'alpha2', 'alpha3', 'numeric', 'numbering']
    Nationality = apps.get_model('mighty', 'nationality')

    with open(conf.csvfile, encoding=conf.encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=conf.delimiter)
        for row in reader:
            obj, create = Nationality.objects.get_or_create(**{field: row[field] for field in fields if row[field]})
            img = '%s/flags/%s.png' % (conf.directory, row['alpha2'].lower())
            if os.path.isfile(img):
                f = open(img, "rb")
                flag = File(f)
                obj.image.save(img, flag, save=True)
            obj.save()

class Migration(migrations.Migration):
    dependencies = [
        ('mighty', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_nationalities),
    ]