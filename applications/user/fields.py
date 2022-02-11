from mighty import fields
from mighty.functions import setting
from mighty.applications.user.apps import UserConfig as conf

search = ('username', 'email', 'last_name', 'first_name')
serializer = ('uid',) + fields.image_url + (
    'username',
    'last_name',
    'first_name',
    'fullname',
    'representation',
    'style',
    'gender',
    'is_staff',
)

if conf.cgu:
    serializer+('cgu',)

if conf.cgv:
    serializer+('cgv',)

invitation = ('last_name', 'first_name', 'email', 'phone', 'user', 'by', 'token', 'status')
profile = fields.image_url + (
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
)

if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
    serializer += ('nationalities',)
    profile += ('all_nationalities',)