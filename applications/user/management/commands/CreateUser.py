from mighty.management import CSVModelCommand
from django.contrib.auth import get_user_model
from mighty.applications.user import username_generator_v2

UserModel = get_user_model()

class Command(CSVModelCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--email', default=None)
        parser.add_argument('--password', default=None)
        parser.add_argument('--username', default=None)
        parser.add_argument('--lastname', default=None)
        parser.add_argument('--firstname', default=None)
        parser.add_argument('--is_superuser', default=False, type=bool)
        parser.add_argument('--is_staff', default=False, type=bool)

    def handle(self, *args, **options):
        self.email = options.get('email')
        self.password = options.get('password')
        self.username = options.get('username')
        self.lastname = options.get('lastname')
        self.firstname = options.get('firstname')
        self.is_superuser = options.get("is_superuser")
        self.is_staff = options.get("is_staff")
        super().handle(*args, **options)

    def do(self):
        if self.csvfile:
            self.loop_qs("on_row")
        else:
            self.create_user_arg()

    def on_row(self, row):
        data = {
            "email": row.get("email"),
            "password": row.get("password"),
            "is_superuser": bool(row.get("is_superuser")),
            "is_staff": bool(row.get("is_staff")),
            "first_name": row.get("firstname"),
            "last_name": row.get("lastname"),
            "username": self.get_username(row)
        }
        self.create_user(data)

    def get_username(self, data):
        if data.get("username"):
            return data["username"]
        elif data.get("firstname") and data.get("lastname"):
            return username_generator_v2(first_name=data.get("firstname"), last_name=data.get("lastname"))
        else:
            return username_generator_v2(email=data.get("email"))

    def create_user_arg(self):
        data = {
            "email": self.email,
            "password": self.password,
            "is_superuser": self.is_superuser,
            "is_staff": self.is_staff,
            "first_name": self.firstname,
            "last_name": self.lastname,
            "username": self.username or username_generator_v2(email=self.email)
        }
        self.create_user(data)

    def create_user(self, data):
        user = UserModel.objects.create_user(**data)
        user.save()
