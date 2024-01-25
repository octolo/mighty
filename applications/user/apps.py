from django.apps import AppConfig
from mighty import over_config
from mighty.functions import setting

class Config:
    #user_or_inivitation_lct = {'app_label': 'mighty', 'model__in': ['user', 'userorinvitation']}
    invitation_enable = True
    invitation_days = 7
    invitation_url = 'http://%(domain)s/user/invitation/%(uid)s/?token=%(token)s'
    cgu = True
    cgv = False
    protect_trashmail = True
    notification_optional_relation = {}

    class ForeignKey:
        missive = 'mighty.Missive'
        invitation = 'mighty.Invitation'
        nationalities = 'mighty.Nationality'
        email = 'mighty.UserEmail'
        phone = 'mighty.UserPhone'
        address = 'mighty.UserAddress'
        user = setting("AUTH_USER_MODEL")
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
        style = ['light',]

over_config(Config, setting("USER"))
class UserConfig(AppConfig, Config):
    name = 'mighty.applications.user'

    def ready(self):
        from . import signals
