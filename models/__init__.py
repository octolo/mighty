from django.conf import settings
from django.db import connection, models

if connection.vendor == 'mysql': from django_mysql.models import JSONField
elif connection.vendor == 'postgresql': from django.contrib.postgres.fields import JSONField
else: 
    from jsonfield import JSONField
class JSONField(JSONField):
    pass

if 'tinymce' in settings.INSTALLED_APPS:
    from tinymce.models import HTMLField
    class HTMLField(HTMLField):
        pass

if 'ckeditor' in settings.INSTALLED_APPS:
    from ckeditor.fields import RichTextField
    class HTMLField(RichTextField):
        pass

if 'mighty.applications.logger' in settings.INSTALLED_APPS:
    from mighty.models.application import logger

if 'mighty.applications.user' in settings.INSTALLED_APPS:
    from mighty.models.applications import user

if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
    from mighty.models.applications import twofactor

if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    from mighty.models.applications import nationality

if 'mighty.applications.grapher' in settings.INSTALLED_APPS:
    from mighty.models.applications import grapher