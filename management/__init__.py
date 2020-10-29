from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned

from mighty import functions
from mighty.apps import MightyConfig as conf
from mighty.applications.logger.apps import LoggerConfig
import datetime, sys, logging
logger = logging.getLogger(__name__)

class Error:
    def __init__(self):
        self.count = 0
        self.errors = {}

    def add(self, key, msg, current_row=False):
        self.count += 1
        if key not in self.errors: self.errors[key] = []
        self.errors[key].append("%s | line: %s" % (msg, current_row)) if current_row else self.errors[key].append(msg)

class BaseCommand(BaseCommand):
    help = 'Command Base override by Mighty'
    position = 0
    prefix_bar = 'Percent'
    current_info = ''

    def get_total(self):
        return self.total if self.total else 0
    
    def set_position(self, pos=1):
        self.position+=pos

    def progress_bar(self, bar_length=20):
        percent = self.position / self.get_total()
        if self.progressbar:
            arrow = '-' * int(round(percent * bar_length)-1) + '>'
            spaces = ' ' * (bar_length - len(arrow))
            sys.stdout.write("\r{0}: [{1}] {2}% ({3}/{4}) {5}".format(
                self.prefix_bar,
                arrow + spaces,
                int(round(percent * 100)),
                self.position,
                self.get_total(),
                self.current_info,
                )
            )
            sys.stdout.flush()
        else:
            sys.stdout.write("\r{0}: {1}% ({2}/{3}) {4}".format(
                self.prefix_bar,
                int(round(percent * 100)),
                self.position,
                self.get_total(),
                self.current_info)
            )
            print()
        if self.position == self.get_total(): print()

    def create_parser(self, prog_name, subcommand, **kwargs):
        self.subcommand = subcommand
        return super().create_parser(prog_name, subcommand)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--total', default=0)
        parser.add_argument('--encoding', default='utf8')
        parser.add_argument('--logfile', default="%s_%s.log" % (str(self.subcommand).lower(), f"{datetime.datetime.now():%Y%m%d_%H%M%S_%f}"))
        parser.add_argument('--progressbar', action="store_true")

    def handle(self, *args, **options):
        self.error = Error()
        self.encoding = options.get('encoding')
        self.logfile = options.get('logfile')
        self.progressbar = options.get('progressbar')
        self.verbosity = options.get('verbosity', 0)
        logger.debug('start')
        self.do()
        logger.debug('end')

    def do(self):
        raise NotImplementedError("Command should implement method do(self)")

class ModelBaseCommand(BaseCommand):
    help = 'Commande Model Base'
    manager = 'objects'
    label = None
    model = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--create', action="store_true")
        parser.add_argument('--label', default=None)
        parser.add_argument('--model', default=None)
        parser.add_argument('--filter', default=None)
        parser.add_argument('--manager', default='objects')
        parser.add_argument('--search', action="store_true")

    def handle(self, *args, **options):
        self.create = options.get('create')
        self.label = options.get('label', self.label)
        self.model = options.get('model', self.model)
        self.manager = options.get('manager', self.manager)
        self.filter = options.get('filter')
        self.search = options.get('search')
        super().handle(*args, **options)

    def get_queryset(self, *args, **kwargs):
        label = kwargs.get('label', self.label)
        model = kwargs.get('model', self.model)
        manager = kwargs.get('manager', self.manager)
        model = functions.get_model(label, model)
        return getattr(model, manager).filter(**dict(x.split(',') for x in self.filter.split(';')) if self.filter else {})

    def do(self):
        self.each_objects()

    def each_objects(self):
        qs = self.get_queryset()
        self.total = len(qs)
        for obj in self.get_queryset():
            self.set_position()
            self.progress_bar()
            self.on_object(obj)

    def on_object(self, object):
        raise NotImplementedError("Command should implement method on_object(self, obj)")
        

        