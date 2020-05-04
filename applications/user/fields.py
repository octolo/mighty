from mighty import fields
from mighty.functions import setting

searchs = ('username', 'email', 'last_name', 'first_name')
params = ('uid', 'gender')
serializer = fields.detail_url + fields.uid + fields.image_url + ('username', 'email', 'last_name', 'first_name', 'last_login', 'get_gender_display')

if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
    params += ('nationalities',)
    serializer += ('nationalities',)