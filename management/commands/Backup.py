import csv
import datetime
import os
import shutil
import tarfile
from itertools import chain

from django.contrib.contenttypes.models import ContentType
from django.db import models

from mighty.apps import MightyConfig as conf
from mighty.management import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--media', default=None)
        parser.add_argument('--contenttype', default='*')
        parser.add_argument('--backupdir', default='backups')
        parser.add_argument('--delimiter', default=';')
        parser.add_argument('--quotechar', default='"')
        parser.add_argument('--quoting', default=csv.QUOTE_ALL)
        parser.add_argument('--mode', default='w')
        parser.add_argument('--uid', action='store_true')
        parser.add_argument('--excludes', default='')
        parser.add_argument('--backup', default='csv,media,cloud')

    def handle(self, *args, **options):
        self.media = options.get('media')
        self.contenttype = options.get('contenttype')
        self.backupdir = options.get('backupdir')
        self.delimiter = options.get('delimiter')
        self.quotechar = options.get('quotechar')
        self.quoting = options.get('quoting')
        self.mode = options.get('mode')
        self.uid = options.get('uid')
        self.excludes = options.get('excludes').split(',')
        self.backup = options.get('backup').split(',')
        super().handle(*args, **options)

    def get_dir(self):
        if not os.path.isdir(self.backupdir): os.makedirs(self.backupdir)
        return self.backupdir

    def get_header(self, model):
        field_names = {field.name for field in model._meta.fields}
        m2mfield_names = {field.name for field in model._meta.many_to_many}
        return list(chain(field_names, m2mfield_names))

    def get_line(self, obj):
        row = []
        field_names = {field.name for field in obj._meta.fields}
        m2mfield_names = {field.name for field in obj._meta.many_to_many}
        for field in field_names:
            if type(obj._meta.get_field(field)) == models.ForeignKey and hasattr(getattr(obj, field), 'uid'):
                row.append(getattr(obj, field).uid)
            else:
                row.append(getattr(obj, field))
        for field in m2mfield_names:
            m2ms = getattr(obj, field).all()
            if m2ms and hasattr(m2ms[0], 'uid'):
                row.append(','.join([str(m2m.uid) for m2m in m2ms]))
            else:
                row.append(','.join([str(m2m.id) for m2m in m2ms]))
        return row

    def backup_csv(self, archive):
        for ct in ContentType.objects.all():
            tablefile = f'{ct.app_label}_{ct.model}.csv'
            fullpath = self.backupdir + f'/{tablefile}'
            model = ct.model_class()
            with open(fullpath, self.mode) as csvfile:
                writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar=self.quotechar, quoting=self.quoting)
                writer.writerow(self.get_header(model))
                for obj in model.objects.all(): writer.writerow(self.get_line(obj))
            archive.add(fullpath, arcname=f'db/{tablefile}')
            os.remove(fullpath)

    def backup_cloud(self, archive):
        cloudstorage = + '/%s' % conf.Directory.cloud
        if os.path.isdir(cloudstorage):
            archive.add(cloudstorage, arcname=conf.Directory.cloud[:-1])
            shutil.rmtree(cloudstorage)

    def do(self):
        self.get_dir()
        with tarfile.open(self.backupdir + '/backup_{}.tar.gz'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), 'w:gz') as archive:
            if 'csv' in self.backup:
                self.backup_csv(archive)
            if 'cloud' in self.backup:
                self.backup_cloud(archive)
