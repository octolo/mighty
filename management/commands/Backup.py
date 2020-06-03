from mighty.management import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--media', default=None)
        parser.add_argument('--contenttype', default='*')

    def handle(self, *args, **options):
        self.media = options.get('media')
        self.contenttype = options.get('contenttype')
        super().handle(*args, **options)

    def do(self):
        for ct in ContentType.objects.all():
            table = '%s_%s' % (ct.app_label, ct.model)
            model = ct.model_class()
            if table == 'mighty_user':
                for field in model._meta.get_fields():
                    if type(field) == models.ManyToManyField:
                        print(field)


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