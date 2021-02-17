from mighty.management import BaseCommand
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--email')
        parser.add_argument('--password')

    def handle(self, *args, **options):
        self.email = options.get('email')
        self.password = options.get('password')
        super().handle(*args, **options)

    def do(self):
        user = UserModel.objects.create_user('root', email=self.email, password=self.password)
        user.is_superuser=True
        user.is_staff=True
        user.save()
