from mighty.management import BaseCommand
from django.template.loader import render_to_string

class Command(BaseCommand):
    context = {}
    service = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--service')
        parser.add_argument('--description', default=None)
        parser.add_argument('--envfile', default=None)
        parser.add_argument('--workingdir', default=None)
        parser.add_argument('--user', default=None)
        parser.add_argument('--group', default=None)
        parser.add_argument('--pid', default=None)
    
    def handle(self, *args, **options):
        self.context = {
            'DESC': options.get('description'),
            'ENVFILE': options.get('envfile'),
            'WORKINGDIRECTORY': options.get('workingdir'),
            'USER': options.get('user'),
            'GROUP': options.get('group'),
            'PIDFILE': options.get('pid'),
        }
        self.service = options.get('service')
        super().handle(*args, **options)

    def do(self):
        if self.service:
            print(render_to_string('services/%s.service' % self.service, self.context))

