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
    'get_gender_display',
    'is_staff',
)

if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
    serializer += ('nationalities',)

invitation = ('last_name', 'first_name', 'email', 'phone', 'user', 'by', 'invitation', 'token', 'status')