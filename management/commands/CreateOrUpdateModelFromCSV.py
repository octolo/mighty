from django.core.management.base import CommandError
from mighty.management import ModelBaseCommand
import csv, os.path

class Command(ModelBaseCommand):
    column_for_current = None

    def add_arguments(self, parser):
        parser.add_argument('--csv')
        parser.add_argument('--delimiter', default=',')
        parser.add_argument('--quotechar', default='"')
        parser.add_argument('--quoting', default=csv.QUOTE_ALL)
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.csvfile = options.get('csv')
        self.delimiter = options.get('delimiter')
        self.quotechar = options.get('quotechar')
        self.quoting = options.get('quoting')
        if not os.path.isfile(self.csvfile):
            raise CommandError('CSV "%s" does not exist' % self.csv)
        super().handle(*args, **options)

    def prepare_fields(self, fields):
        if hasattr(self, 'fields'):
            ofields = self.fields
            rfields = {value: key for key, value in self.fields.items()}
            self.fields = {}
            self.reverse = {}
            for field in fields:
                self.fields[field] = ofields[field] if field in ofields else field
                if field in rfields:
                    self.reverse[rfields[field]] = field
                else:
                    self.reverse[field] = field
            self.fields = {field: field for field in fields}
        else:
            self.fields = self.reverse = {field: field for field in fields}

    def do(self):
        self.total = len(open(self.csvfile).readlines())-1
        with open(self.csvfile, encoding=self.encoding) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            self.prepare_fields(reader.fieldnames)
            for row in reader:
                self.set_position()
                if self.column_for_current:
                    self.current_info = row[self.reverse['extension']]
                self.progress_bar()
                self.on_row(row)

    def on_row(self, row):
        raise NotImplementedError("Command should implement method on_object(self, obj)")
        