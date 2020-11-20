default_app_config = 'mighty.applications.user.apps.UserConfig'

from django.conf import settings
from django.contrib.auth import get_user_model
from mighty.applications.user.apps import UserConfig as conf
import uuid

def username_generator(base_username):
    UserModel = get_user_model()
    prefix = "".join([l for l in base_username if l.isalpha()])
    prefix = prefix[:3] if len(prefix) >= 3 else prefix
    exist = True
    while exist:
        username = '%s%s' % ('%s-' % prefix if prefix else '', str(uuid.uuid4())[:8])
        username = username.lower()
        try:
            UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            exist = False
    return username

def get_form_fields():
    return conf.Field.required + (conf.Field.username,)
