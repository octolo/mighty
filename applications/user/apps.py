from django.apps import AppConfig

from mighty import over_config
from mighty.functions import setting


class Config:
    cgu = True
    cgv = False
    protect_trashmail = True
    notification_optional_relation = {}

    class ForeignKey:
        missive = 'mighty.Missive'
        nationalities = 'mighty.Nationality'
        # Need cleanup
        email = 'mighty.UserEmail'
        email_related_name = 'user_email'
        email_related_name_attr = 'user_email'
        email_field = 'default'
        email_primary = 'default'
        phone = 'mighty.UserPhone'
        address = 'mighty.UserAddress'
        user = setting('AUTH_USER_MODEL')
        optional = False
        optional2 = False
        optional3 = False
        optional4 = False
        optional5 = False
        raw_id_fields = ()

    class Field:
        username = 'email'
        required = ('cgu',)
        optional = ('phone',)
        style = ['light']


over_config(Config, setting('USER'))


class UserConfig(AppConfig, Config):
    name = 'mighty.applications.user'

    def ready(self):
        from . import signals  # noqa
