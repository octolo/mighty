from mighty.management import ModelBaseCommand

class Command(ModelBaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--filetype', default='txt')

    def handle(self, *args, **options):
        self.filetype = options.get('filetype')
        super().handle(*args, **options)

    def on_object(self, obj):
        print(obj.file_format(fileformat=self.filetype))