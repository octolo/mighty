import json
import os

from django.core.management.base import CommandError

from mighty.management import ModelBaseCommand
from mighty.models import Nationality, TranslateDict, Translator


class Command(ModelBaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--json', default=None)
        parser.add_argument('--folder', default=None)
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.json = options.get('json')
        self.folder = options.get('folder')
        if self.json or self.folder:
            super().handle(*args, **options)
        else:
            raise CommandError('--json or --folder required')

    def makeJob(self):
        if self.json:
            self.load_jsonfile(self.json)
        else:
            self.load_jsonfolder(self.folder)

    def load_jsonfile(self, jsonfile):
        name = os.path.splitext(os.path.basename(jsonfile))[0]
        tr, _status = Translator.objects.get_or_create(name=name)
        with open(jsonfile, encoding=self.encoding) as json_file:
            languages = json.load(json_file)
            for lang, translates in languages.items():
                nat = Nationality.objects.get(alpha2__icontains=lang.split('_')[-1])
                td, _status = TranslateDict.objects.get_or_create(language=nat, precision=lang, translator=tr)
                td.translates = translates
                td.save()

    def load_jsonfolder(self, folder):
        qs = []
        for (dirpath, _dirnames, filenames) in os.walk(folder):
            qs.extend(os.path.join(dirpath, file) for file in filenames if file.endswith('.json'))
        self.each_objects(qs)

    def on_object(self, obj):
        self.load_jsonfile(obj)
