from django.core.files import File
from mighty.management.commands.CreateOrUpdateModelFromCSV import Command

from mighty.applications.nationality.apps import NationalityConfig

import os.path

class Command(Command):
    testconfig = ["none",]
    fields_retrieve = ['country','alpha2','alpha3']
    fields_associates = {
        'country': 'Country',
        'alpha2': 'Alpha2',
        'alpha3': 'Alpha3',
        'numeric': 'Numeric',
    }

    def after_line(self, line, obj):
        src = '%s/flags' % NationalityConfig.directory
        flagalpha2 = '%s/%s.png' % (src, line["Alpha2"].lower())
        if os.path.isfile(flagalpha2):
            f = open(flagalpha2, "rb")
            flag = File(f)
            obj.image.save(flagalpha2, flag, save=True)