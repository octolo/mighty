from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from mighty.apps import MightyConfig
from mighty.models import Twofactor, Missive
from mighty.applications.twofactor import translates as _
from mighty.applications.twofactor.apps import TwofactorConfig as conf
from mighty.applications.messenger import choices

import datetime, logging

logger = logging.getLogger(__name__)
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
                    earlier, now = self.earlier
                    code = Twofactor.objects.get(user=user, code=password, date_create__range=(earlier,now), is_consumed=False)
                    code.is_consumed = True
                    code.save()
                    user.get_client_ip(request)
                    user.get_user_agent(request)
                    return user
                except Exception as e:
                    UserModel().set_password(password)
    
    @property
    def earlier(self):
        now = datetime.datetime.now()
        earlier = now - datetime.timedelta(minutes=conf.minutes_allowed)
        return earlier, now

    def get_object(self, user, target, mode, backend, **kwargs):
        earlier, now = self.earlier
        prepare = {
            "mode": mode,
            "email_or_phone": target,
            "user": user,
            "backend": backend,
            "date_create__range": (earlier,now),
            "is_consumed": False,
        }
        prepare.update(**kwargs)
        return Twofactor.objects.get_or_create(**prepare)

    def by(self, mode, user, target, backend_path):
        if hasattr(self, 'send_%s' % mode):
            twofactor, created = self.get_object(user, target, getattr(choices, 'MODE_%s' % mode.upper()), backend_path)
            logger.info("code twofactor (%s): %s" % (target, twofactor.code), extra={'user': user, 'app': 'twofactor'})
            return getattr(self, 'send_%s' % mode)(twofactor, user, target)
        return False
        
    def send_sms(self, obj, user, target):
        missive = Missive(**{
            "user_or_invitation": user.missives.content_type,
            "object_id": user.id,
            "target": target,
            "mode": choices.MODE_SMS,
            "subject": 'subject: Code',
            "txt": _.tpl_txt %(MightyConfig.site, str(obj.code)),
        })
        missive.save()
        return missive.status

    def send_email(self, obj, user, target):
        missive = Missive(**{
            "user_or_invitation": user.missives.content_type,
            "object_id": user.id,
            "target": target,
            "subject": 'subject: Code',
            "html": _.tpl_html % (MightyConfig.site, str(obj.code)),
            "txt": _.tpl_txt % (MightyConfig.site, str(obj.code)),
        })
        missive.save()
        return missive.status