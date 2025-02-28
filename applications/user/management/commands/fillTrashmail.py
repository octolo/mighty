
from mighty.management import CSVModelCommand
from mighty.models import Trashmail


class Command(CSVModelCommand):
    def on_row(self, row):
        Trashmail.objects.get_or_create(domain=row['domain'])
