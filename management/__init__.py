import csv
import datetime
import os
import os.path
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from django.utils.module_loading import import_string

from mighty.applications.logger import EnableLogger
from mighty.applications.user.apps import UserConfig
from mighty.apps import MightyConfig as conf
from mighty.functions import get_model, request_kept
from mighty.readers import ReaderXLS as ReaderXLS
from mighty.readers import ReaderXLSX


class BaseCommand(BaseCommand, EnableLogger):
    importer = None
    importer_required = False
    importer_path = None
    default_string_arguments = ('fkmodel', 'm2mmodel')
    default_boolean_arguments = ('loader', 'test', 'progressbar')
    default_integer_arguments = ()
    string_arguments = ()
    boolean_arguments = ()
    integer_arguments = ()
    help = 'Command Base override by Mighty'
    position = 0
    prefix_bar = 'Percent'
    current_info = ''
    splitter = ','
    errors = []
    in_test = False
    loader = False
    userlog_cache = None
    ftotal = 'total'
    total = 0
    command_date_start = timezone.now()

    def init_importer(self, importer):
        self.importer = import_string(self.importer_path + f'.importers.{importer}.Importer')()

    def get_object_unique_from_qs(self, qs, assoc, values):
        for k, v in assoc.items():
            if values.get(k):
                if v == 'pos':
                    return qs[int(values.get(k))]
                return qs.get(**{v: values.get(k)})
        return None

    @property
    def user_model(self):
        return get_user_model()

    def get_user(self, info, forlog=False):
        if info:
            try:
                Qparams = Q(id=int(info))
            except ValueError:
                Qparams = Q(**{UserConfig.ForeignKey.email_related_name + '__email': info}) | Q(user_phone__phone=info) | Q(username=info)
            try:
                return self.user_model.objects.get(Qparams)
            except self.user_model.DoesNotExist:
                pass
        return self.user_model.objects.filter(is_superuser=True).first() if forlog else None

    def set_position(self, pos=1):
        self.position += pos

    def get_current_info(self):
        return self.current_info

    def progress_bar(self, bar_length=20):
        total = getattr(self, self.ftotal)
        if self.verbosity > 0 and total:
            percent = self.position / total
            if self.progressbar:
                arrow = '-' * int(round(percent * bar_length) - 1) + '>'
                spaces = ' ' * (bar_length - len(arrow))
                sys.stdout.write(f'\r{self.prefix_bar}: [{arrow + spaces}] {round(percent * 100)}% ({self.position}/{total}) {self.get_current_info()}'
                )
                sys.stdout.flush()
            else:
                sys.stdout.write(f'\r{self.prefix_bar}: {round(percent * 100)}% ({self.position}/{total}) {self.get_current_info()}'
                )
                print()
            if self.position == total: print()

    def create_parser(self, prog_name, subcommand, **kwargs):
        self.subcommand = subcommand
        return super().create_parser(prog_name, subcommand)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--importer', type=str, help='Importer type', required=self.importer_required)
        parser.add_argument('--logfile', default='{}_{}.log'.format(str(self.subcommand).lower(), f'{datetime.datetime.now():%Y%m%d_%H%M%S_%f}'))
        parser.add_argument('--encoding', default='utf8')
        parser.add_argument('--userlog', default=None)
        for field in self.string_arguments + self.default_string_arguments:
            parser.add_argument(f'--{field}', default=None)
        for field in self.integer_arguments + self.default_integer_arguments:
            parser.add_argument(f'--{field}', default=0)
        for field in self.boolean_arguments + self.default_boolean_arguments:
            parser.add_argument(f'--{field}', action='store_true')

    @property
    def default_fields(self):
        return self.default_string_arguments + self.default_integer_arguments + self.default_boolean_arguments

    @property
    def working_fields(self):
        return self.string_arguments + self.integer_arguments + self.boolean_arguments

    @property
    def auto_fields(self):
        return self.default_fields + self.working_fields + ('logfile', 'encoding')

    def handle(self, *args, **options):
        self.importer = options.get('importer')
        for field in self.auto_fields:
            setattr(self, field, options.get(field))
        self.verbosity = options.get('verbosity', 0)
        self.userlog_cache = self.get_user(options.get('userlog'))
        self.logger.debug('start')
        self.makeJob()
        self.showErrors()
        self.logger.debug('end')

    def prepare_request(self):
        class request:
            user = self.userlog_cache
        request_kept.request = request

    def makeJob(self):
        self.prepare_request()
        self.before_job()
        self.do()
        self.after_job()

    def before_job(self): pass
    def after_job(self): pass

    def showErrors(self):
        for error in self.errors:
            self.logger.info(error)

    def do(self):
        raise NotImplementedError('Command should implement method do(self)')


class ModelBaseCommand(BaseCommand):
    help = 'Commande Model Base'
    manager = 'objects'
    label = None
    model = None
    filter = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--create', action='store_true')
        parser.add_argument('--label', default=self.label)
        parser.add_argument('--model', default=self.model)
        parser.add_argument('--filter', default=None)
        parser.add_argument('--manager', default=self.manager)
        parser.add_argument('--search', action='store_true')

    def handle(self, *args, **options):
        self.create = options.get('create')
        self.label = options.get('label')
        self.model = options.get('model')
        self.manager = options.get('manager')
        self.filter = options.get('filter')
        self.search = options.get('search')
        super().handle(*args, **options)

    @property
    def model_use(self, *args, **kwargs):
        if self.model and type(self.model) != str:
            return self.model
        label = kwargs.get('label', self.label)
        model = kwargs.get('model', self.model)
        self.model = get_model(label, model)
        return self.model

    def get_queryset_filter(self):
        return dict(x.split(',') for x in self.filter.split(';')) if self.filter else {}

    def get_queryset(self, *args, **kwargs):
        manager = kwargs.get('manager', self.manager)
        model = self.model_use
        return getattr(model, manager).filter(**self.get_queryset_filter())

    def get_current_info(self):
        return self.current_object

    def do(self):
        self.each_objects(self.get_queryset())

    def each_objects(self, qs, do='on_object'):
        self.position = 0
        self.total = len(qs)
        for obj in qs:
            self.current_object = obj
            self.set_position()
            if self.loader or self.progressbar:
                self.progress_bar()
            getattr(self, do)(obj)

    def on_object(self, object):
        raise NotImplementedError('Command should implement method on_object(self, obj)')


class ImportModelCommand(ModelBaseCommand):
    _reader = None
    _total = None
    current_row = None
    column_for_current = None
    fields = {}
    reverse = None
    real_values = {}
    required_fields = []
    need_reset_reader = False
    ftotal = 'import_total'
    stop_loop = False

    def reset_reader(self):
        self.position = 0
        self.need_reset_reader = True

    def is_required(self, name):
        return (name in self.required_fields)

    def field(self, name):
        try:
            return self.current_row[self.reverse[name]]
        except KeyError:
            for key in self.current_row:
                if key and key.lower() == name:
                    return self.current_row[key]
        if self.is_required(name):
            raise KeyError(name + ' not found')
        return None

    def real_value(self, value):
        if value and value.lower() in self.real_values:
            return self.real_values[value.lower()]
        return value

    @property
    def reader(self):
        raise NotImplementedError('Command should implement property reader')

    @property
    def import_total(self):
        raise NotImplementedError('Command should implement property total')

    def prepare_fields(self, fields):
        if hasattr(self, 'fields'):
            ofields = self.fields
            self.fields = {}
            for field in fields:
                self.fields[field] = ofields.get(field, field)
            self.reverse = {v: k for k, v in self.fields.items()}
        else:
            self.fields = self.reverse = {field: field for field in fields}

    def do(self):
        self.prepare_fields(self.reader.fieldnames)
        self.loop_qs('on_row')

    def get_current_info(self):
        return self.current_row

    def loop_qs(self, do):
        self.position = 0
        for row in self.reader:
            self.current_row = row
            self.set_position()
            if self.loader or self.progressbar:
                self.progress_bar()
            getattr(self, do)(row)

    def on_row(self, row):
        raise NotImplementedError('Command should implement method on_object(self, obj)')

# class XLSModelCommand(ImportModelCommand):
#    xlsmandatory = True
#
#    def check_xlsfile(self, mandatory):
#        if self.xlsxfile and os.path.isfile(self.xls):
#            return True
#        if mandatory:
#            raise CommandError('file %s" does not exist' % self.xlsx)
#        return False
#
#    def add_arguments(self, parser):
#        parser.add_argument('--sheet')
#        parser.add_argument('--xls')
#        super().add_arguments(parser)
#
#    def handle(self, *args, **options):
#        self.xlsfile = options.get('xls')
#        self.sheet = options.get('sheet')
#        self.check_xlsfile(self.xlsmandatory)
#        super().handle(*args, **options)
#
#    @property
#    def reader(self):
#        if not self._reader or self.need_reset_reader:
#            self._reader = ReaderXLS(self.xlsfile, self.sheet)
#            self.need_reset_reader = False
#        return self._reader
#
#    @property
#    def import_total(self):
#        return self.reader.total-1


class XLSXModelCommand(ImportModelCommand):
    xlsxmandatory = True

    def check_xlsxfile(self, mandatory):
        if self.xlsxfile and os.path.isfile(self.xlsxfile):
            return True
        if mandatory:
            raise CommandError(f'file {self.xlsx}" does not exist')
        return False

    def add_arguments(self, parser):
        parser.add_argument('--sheet')
        parser.add_argument('--xlsx')
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.xlsxfile = options.get('xlsx')
        self.sheet = options.get('sheet')
        self.check_xlsxfile(self.xlsxmandatory)
        super().handle(*args, **options)

    @property
    def reader_xlsx(self):
        if not self._reader or self.need_reset_reader:
            self._reader = ReaderXLSX(self.xlsxfile, self.sheet)
            self.need_reset_reader = False
        return self._reader

    @property
    def reader(self):
        return self.reader_xlsx

    @property
    def import_total(self):
        return self.reader.total - 1


class CSVModelCommand(ImportModelCommand):
    csvmandatory = True

    def check_csvfile(self, mandatory):
        if self.csvfile and os.path.isfile(self.csvfile):
            return True
        if mandatory:
            raise CommandError(f'CSV "{self.csvfile}" does not exist')
        return False

    def add_arguments(self, parser):
        parser.add_argument('--skiprows', type=int, default=0, help='Skip rows')
        parser.add_argument('--csv', type=str, help='CSV file to import')
        parser.add_argument('--delimiter', default=',')
        parser.add_argument('--quotechar', default='"')
        parser.add_argument('--quoting', default=csv.QUOTE_ALL)
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.skiprows = options.get('skiprows')
        self.csvfile = options.get('csv')
        self.delimiter = options.get('delimiter')
        self.quotechar = options.get('quotechar')
        self.quoting = options.get('quoting')
        self.check_csvfile(self.csvmandatory)
        super().handle(*args, **options)

    @property
    def reader_csv(self):
        if not self._reader or self.need_reset_reader:
            csvfile = open(self.csvfile, encoding=self.encoding)
            for _i in range(self.skiprows): next(csvfile)
            self._reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            self.need_reset_reader = False
        return self._reader

    @property
    def reader(self):
        return self.reader_csv

    @property
    def import_total(self):
        if not self._total:
            self._total = len(open(self.csvfile, encoding='utf-8').readlines()) - 1
        return self._total


class AnyDataFileCommand(XLSXModelCommand, CSVModelCommand):
    xlsmandatory = False
    xlsxmandatory = False
    csvmandatory = False

    @property
    def has_file_data(self):
        return any([self.xlsxfile, self.csvfile])

    @property
    def reader(self):
        if self.xlsxfile:
            return self.reader_xlsx
        if self.csvfile:
            return self.reader_csv
        return self.get_queryset()

    @property
    def import_total(self):
        if self.xlsxfile:
            return super(self, XLSXModelCommand).import_total
        if self.csvfile:
            return super(self, CSVModelCommand).import_total
        return self.get_queryset().count()


class ImporterCommand(AnyDataFileCommand):
    help = 'Command importer'
    impoter_required = True
    importer_path = None

    def get_queryset(self, *args, **kwargs):
        if hasattr(self.importer, 'get_queryset'):
            return self.importer.get_queryset(*args, **kwargs).filter(**self.get_queryset_filter())
        return super().get_queryset(*args, **kwargs)

    @property
    def reader(self):
        if self.xlsxfile:
            return self.reader_xlsx
        if self.csvfile:
            return self.reader_csv
        return self.get_queryset()

    def do(self):
        self.loop_qs('on_data')

    def before_job(self):
        self.action = self.importer
        self.init_importer(self.importer)
        if hasattr(self, 'before_' + self.action):
            getattr(self, 'before_' + self.action)()

    def on_data(self, data):
        if hasattr(self, self.action):
            getattr(self, self.action)(data)
        else:
            self.do_action(self.action, data)

    def do_action(self, action, data):
        raise NotImplementedError('Command should implement method do_action(self, action, data)')
