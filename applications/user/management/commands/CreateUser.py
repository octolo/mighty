from mighty.management import CSVModelCommand
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class Command(CSVModelCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--email', default=None)
        parser.add_argument('--password', default=None)
        parser.add_argument('--username', default=None)
        parser.add_argument('--lastname', default=None)
        parser.add_argument('--firstname', default=None)
        parser.add_argument('--is_superuser', default=False)
        parser.add_argument('--is_staff', default=False)


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
        fake = UserModel(email=row["email"])
        data = {
            "email": row["email"],
            "password": row["password"],
            "is_superuser": bool(row["is_superuser"]),
            "is_staff": bool(row["is_staff"]),
        }
        if row["firstname"]: data['first_name'] = row["firstname"]
        if row["lastname"]: data['last_name'] = row["lastname"]
        if "username" in row:
            data["username"] = row["username"] or fake.gen_username()
        else:
            data["username"] = fake.gen_username()
        self.create_user(data)

    def create_user_arg(self):
        fake = UserModel(email=self.email)
        data = {
            "email": self.email,
            "password": self.password,
            "is_superuser": self.is_superuser,
            "is_staff": self.is_staff,
            "username": self.username or fake.gen_username(),
        }
        if self.firstname: data['first_name'] = self.firstname
        if self.lastname: data['last_name'] = self.lastname
        self.create_user(data)

    def create_user(self, data):
        user = UserModel.objects.create_user(**data)
        user.save()
