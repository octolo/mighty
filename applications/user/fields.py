from mighty import fields
from mighty.functions import setting

search = ('username', 'email', 'last_name', 'first_name')
params = ('uid', 'gender')
serializer = fields.detail_url + fields.image_url + ('username', 'email', 'last_name', 'first_name', 'last_login', 'get_gender_display')

if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
    params += ('nationalities',)
    serializer += ('nationalities',)

user_or_invitation = ('last_name', 'first_name', 'email', 'phone', 'user')