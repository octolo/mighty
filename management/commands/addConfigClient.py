import json
import os.path

from django.core.management.base import CommandError

from mighty.management import ModelBaseCommand
from mighty.models import ConfigClient


class Command(ModelBaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--name')
        parser.add_argument('--json')
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.name = options.get('name')
        self.json = options.get('json')
        if not os.path.isfile(self.json):
            raise CommandError(f'JSON "{self.json}" does not exist')
        super().handle(*args, **options)

    def makeJob(self):
        self.do()

    def do(self):
        with open(self.json, encoding=self.encoding) as json_file:
            conf, _status = ConfigClient.objects.get_or_create(name=self.name)
            conf.config = json.load(json_file)
            conf.save()
