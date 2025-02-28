from django.db import models

from mighty import fields
from mighty.applications.user import choices as _c
from mighty.applications.user import translates as _
from mighty.applications.user.apps import UserConfig as conf
from mighty.functions import setting

search = ('username', 'email', 'last_name', 'first_name')
serializer = (
    'uid',
    *fields.image_url,
    'username',
    'last_name',
    'first_name',
    'fullname',
    'representation',
    'style',
    'gender',
    'is_staff',
    'sentry_replay',
)
if conf.cgu:
    (*serializer, 'cgu')
if conf.cgv:
    (*serializer, 'cgv')

profile = (
    *fields.image_url,
    'username',
    'last_name',
    'first_name',
    'fullname',
    'representation',
    'style',
    'gender',
    'is_staff',
    'language_pref',
    'is_first_login',
    'sentry_replay',
)

if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
    serializer += ('nationalities',)
    profile += ('all_nationalities',)


class GenderField(models.CharField):
    description = _.gender_desc

    def __init__(self, *args, **kwargs):
        kwargs['verbose_name'] = _.gender
        kwargs['max_length'] = 1
        kwargs['choices'] = _c.GENDER
        kwargs['default'] = None
        super().__init__(*args, **kwargs)
