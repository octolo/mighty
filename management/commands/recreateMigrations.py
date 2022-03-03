from mighty.management import BaseCommand
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
    path = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--path')
    
    def handle(self, *args, **options):
        self.path = options.get('path')
        super().handle(*args, **options)

    def do(self):
        MigrationRecorder.Migration.objects.all().delete()
        print("1. Recreate all folders migrations needed (with __init__.py)")
        print("2. Do this 2 commands : ")
        print("python manage.py makemigrations")
        print("python manage.py migrate --fake")