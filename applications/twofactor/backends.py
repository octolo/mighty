from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator, ValidationError
from django.db.models import Q

from mighty.apps import MightyConfig
from mighty.models import Twofactor, Missive
from mighty.applications.twofactor import translates as _
from mighty.applications.twofactor.apps import TwofactorConfig as conf
from mighty.applications.messenger import choices


from phonenumber_field.validators import validate_international_phonenumber
import datetime, logging

logger = logging.getLogger(__name__)
UserModel = get_user_model()

class TwoFactorBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        field_type = kwargs.get('field_type', None)
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            if field_type == 'uid' and hasattr(UserModel, 'uid'):
                user = UserModel.objects.get(uid=username)
            else:
                username = username.lower()
                user = UserModel.objects.get(Q(user_email__email=username)|Q(user_phone__phone=username)|Q(username=username))
                #user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if self.user_can_authenticate(user):
                try:
                    earlier, now = self.earlier
                    code = Twofactor.objects.get(user=user, code=password, date_create__range=(earlier,now), is_consumed=False)
                    code.is_consumed = True
                    code.save()
                    if hasattr(request, 'META'):
                        user.get_client_ip(request)
                        user.get_user_agent(request)
                    return user
                except Exception as e:
                    UserModel().set_password(password)
    
    def get_user_target(self, target):
        return UserModel.objects.get(Q(user_email__email=target)|Q(user_phone__phone=target)|Q(username=target))

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

    def by(self, target, backend_path):
        try:
            validator = EmailValidator()
            user = self.get_user_target(target)

            try:
                validator(target)
                mode = choices.MODE_EMAIL
            except ValidationError:
                validate_international_phonenumber(target)
                mode = choices.MODE_SMS

            twofactor, created = self.get_object(user, target, mode, backend_path)
            logger.info("code twofactor (%s): %s" % (target, twofactor.code), extra={'user': user, 'app': 'twofactor'})
            if mode == choices.MODE_EMAIL:
                return self.send_email(twofactor, user, target)
            elif mode == choices.MODE_SMS:
                return self.send_sms(twofactor, user, target)
        except UserModel.DoesNotExist:
            pass
        except ValidationError:
            pass
        return False
        
    def send_sms(self, obj, user, target):
        missive = Missive(**{
            "content_type": user.missives.content_type,
            "object_id": user.id,
            "target": target,
            "mode": choices.MODE_SMS,
            "subject": _.tpl_subject % {'domain': MightyConfig.domain.upper()},
            "txt": _.tpl_txt % {'domain': MightyConfig.domain, 'code': str(obj.code)},
        })
        missive.save()
        return missive

    def send_email(self, obj, user, target):
        from django.template.loader import render_to_string
        missive = Missive(**{
            "content_type": user.missives.content_type,
            "object_id": user.id,
            "target": target,
            "subject": _.tpl_subject % {'domain': MightyConfig.domain.upper()},
            "html": render_to_string(conf.email_code, {'domain': MightyConfig.domain.upper(), 'code': str(obj.code)}),
            "txt": _.tpl_txt % {'domain': MightyConfig.domain.upper(), 'code': str(obj.code)},
        })
        missive.save()
        return missive
