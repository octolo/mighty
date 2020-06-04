from mighty.management import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import models
from itertools import chain
import datetime, csv, os

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--media', default=None)
        parser.add_argument('--contenttype', default='*')
        parser.add_argument('--backupdir', default='backups')
        parser.add_argument('--delimiter', default=';')
        parser.add_argument('--quotechar', default='"')
        parser.add_argument('--quoting', default=csv.QUOTE_MINIMAL)
        parser.add_argument('--mode', default='w')

    def handle(self, *args, **options):
        self.media = options.get('media')
        self.contenttype = options.get('contenttype')
        self.backupdir = options.get('backupdir')
        self.delimiter = options.get('delimiter')
        self.quotechar = options.get('quotechar')
        self.quoting = options.get('quoting')
        self.mode = options.get('mode')
        super().handle(*args, **options)

    def get_dir(self):
        if not os.path.isdir(self.backupdir): os.makedirs(self.backupdir)
        return self.backupdir

    def get_header(self, model):
        field_names = set([field.name for field in model._meta.fields])
        m2mfield_names = set([field.name for field in model._meta.many_to_many])
        return list(chain(field_names, m2mfield_names))

    def get_line(self, obj):
        row = []
        field_names = set([field.name for field in obj._meta.fields])
        m2mfield_names = set([field.name for field in obj._meta.many_to_many])
        row += [getattr(obj, field) for field in field_names]
        row += [getattr(obj, field).values_list('id', flat=True) for field in m2mfield_names]
        return row

    def do(self):
        self.get_dir()
        date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        for ct in ContentType.objects.all():
            table = '%s_%s' % (ct.app_label, ct.model)
            model = ct.model_class()
            with open('%s/%s_%s.csv' % (self.backupdir, table, date), self.mode) as csvfile:
                writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar=self.quotechar, quoting=self.quoting)
                writer.writerow(self.get_header(model))
                for obj in model.objects.all(): writer.writerow(self.get_line(obj))


#import csv
#from django.http import HttpResponse
#from setuptools.compat import unicode


#def export_as_csv_action(description="Export selected objects as CSV file",
#						 fields=None, exclude=None, header=True):
#	"""
#	This function returns an export csv action
#	'fields' and 'exclude' work like in django ModelForm
#	'header' is whether or not to output the column names as the first row
#	"""
#
#	from itertools import chain
#
#	def export_as_csv(modeladmin, request, queryset):
#		"""
#		Generic csv export admin action.
#		based on http://djangosnippets.org/snippets/2369/
#		"""
#		opts = modeladmin.model._meta
#		field_names = set([field.name for field in opts.fields])
#		many_to_many_field_names = set([many_to_many_field.name for many_to_many_field in opts.many_to_many])
#		if fields:
#			fieldset = set(fields)
#			field_names = field_names & fieldset
#		elif exclude:
#			excludeset = set(exclude)
#			field_names = field_names - excludeset
#
#		response = HttpResponse(content_type='text/csv')
#		response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
#
#		writer = csv.writer(response)
#		if header:
#			writer.writerow(list(chain(field_names, many_to_many_field_names)))
#		for obj in queryset:
#			row = []
#			for field in field_names:
#				row.append(unicode(getattr(obj, field)))
#			for field in many_to_many_field_names:
#				row.append(unicode(getattr(obj, field).all()))
#
#			writer.writerow(row)
#		return response
#	export_as_csv.short_description = description
#	return export_as_csv