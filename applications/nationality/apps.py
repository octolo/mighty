import csv
import os.path

from django.apps import AppConfig
from django.conf import settings

from mighty import over_config


class Config:
    directory = os.path.dirname(os.path.realpath(__file__))
    csvfile = f'{directory}/countries.csv'
    encoding = 'utf8'
    delimiter = ','
    quotchar = '"'
    quoting = csv.QUOTE_ALL
    default = 'fr'
    availables = ['fr']


if hasattr(settings, 'NATIONALITY'):
    over_config(Config, settings.NATIONALITY)


class NationalityConfig(AppConfig, Config):
    name = 'mighty.applications.nationality'
