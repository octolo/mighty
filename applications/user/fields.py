from mighty import fields
from mighty.functions import setting

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
)

if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
    serializer += ('nationalities',)
    profile += ('all_nationalities',)