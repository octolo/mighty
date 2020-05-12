from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from mighty.functions import logger
from mighty.models.applications.twofactor import Twofactor
from mighty.applications.twofactor import translates as _
from mighty.applications.twofactor.models import (
    STATUS_PREPARE, STATUS_SENT, STATUS_RECEIVED, STATUS_ERROR,
    MODE_EMAIL, MODE_SMS)

import datetime


UserModel = get_user_model()
class TwoFactorBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(uid=username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if self.user_can_authenticate(user):
                try:
                    code = Twofactor.objects.get(user=user, code=password)
                    code.is_consumed = True
                    code.save()
                    if hasattr(request, 'META'): user.get_client_ip(request)
                    return user
                except Exception as e:
                    UserModel().set_password(password)

    def send_sms(self, user, backend_path):
        now = datetime.datetime.now()
        earlier = now - datetime.timedelta(minutes=1)
        twofactor, created = Twofactor.objects.get_or_create(user=user, is_consumed=False, mode=MODE_SMS, backend=backend_path, date_create__range=(earlier,now))
        sms = _.tpl_txt %(settings.TWOFACTOR['site'], twofactor.code)
        logger("twofactor", "info", "send sms: %s" % twofactor.code, user)
        twofactor.txt = sms
        twofactor.backend = backend_path
        twofactor.save()
        return True

    def check_sms(self, email):
        response = sms.response
        return response

    def send_email(self, user, backend_path):
        now = datetime.datetime.now()
        earlier = now - datetime.timedelta(minutes=1)
        twofactor, created = Twofactor.objects.get_or_create(user=user, is_consumed=False, mode=MODE_EMAIL, backend=backend_path, date_create__range=(earlier,now))
        subject = _.tpl_subject % settings.TWOFACTOR['site']
        html = _.tpl_html % (settings.TWOFACTOR['site'], str(twofactor.code))
        txt = _.tpl_txt %(settings.TWOFACTOR['site'], str(twofactor.code))
        logger("twofactor", "info", "send email: %s" % str(twofactor.code), user)
        twofactor.subject=subject
        twofactor.html=html
        twofactor.txt=txt
        twofactor.backend = backend_path
        twofactor.save()
        return True

    def check_email(self, user, backend_path):
        response = email.response
        return response