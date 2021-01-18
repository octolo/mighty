from django.core.management.base import CommandError
from mighty.management import ModelBaseCommand
from mighty.models import Translator, TranslateDict, Nationality
import os.path, json

class Command(ModelBaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--name', default=None)
        parser.add_argument('--json')
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.name = options.get('name')
        self.json = options.get('json')
        if not os.path.isfile(self.json):
            raise CommandError('JSON "%s" does not exist' % self.json)
        super().handle(*args, **options)

    def get_name(self):
        if not self.name:
            self.name = os.path.basename(self.json)
            self.name = os.path.splitext(self.name)[0]
        return self.name

    def makeJob(self):
        self.do()

    def do(self):
        tr, status = Translator.objects.get_or_create(name=self.get_name())
        with open(self.json, encoding=self.encoding) as json_file:
            languages = json.load(json_file)
            for lang, translates in languages.items():
                nat = Nationality.objects.get(alpha2__icontains=lang.split('_')[-1])
                td, status = TranslateDict.objects.get_or_create(language=nat, precision=lang, translator=tr)
                td.translates = translates
                td.save()
