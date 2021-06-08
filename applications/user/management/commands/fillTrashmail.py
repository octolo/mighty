from django.core.management.base import CommandError
from mighty.management import CSVModelCommand
from mighty.models import Trashmail
import csv, os.path

class Command(CSVModelCommand):
    def on_row(self, row):
        Trashmail.objects.get_or_create(domain=row['domain'])