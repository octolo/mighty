from mighty.management import BaseCommand
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--email')
        parser.add_argument('--password')
        parser.add_argument('--username')
        parser.add_argument('--lastname')
        parser.add_argument('--firstname')

    def handle(self, *args, **options):
        self.email = options.get('email')
        self.password = options.get('password')
        self.username = options.get('username')
        self.lastname = options.get('lastname')
        self.firstname = options.get('firstname')
        super().handle(*args, **options)

    def do(self):
        data = {"email": self.email, "password": self.password }
        if self.firstname: data['first_name'] = self.firstname
        if self.lastname: data['last_name'] = self.lastname
        fake = UserModel(email=self.email)
        if self.username: 
            user = UserModel.objects.create_user(self.username, **data)
        else:
            user = UserModel.objects.create_user(fake.gen_username(), **data)
        user.is_superuser=True
        user.is_staff=True
        user.save()
