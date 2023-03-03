from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator, ValidationError
from django.db.models import Q
from django.utils import timezone
from django.template.loader import render_to_string

from mighty.apps import MightyConfig
from mighty.models import Twofactor, Missive
from mighty.applications.twofactor import translates as _, SpamException, CantIdentifyError, PhoneValidator
from mighty.applications.twofactor.apps import TwofactorConfig as conf
from mighty.applications.messenger import choices

from phonenumber_field.validators import validate_international_phonenumber
import datetime, logging, string

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
                username = self.clean_target(username)
                user = UserModel.objects.get(Q(user_email__email__iexact=username)|Q(user_phone__phone=username)|Q(username=username))
                #user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if self.user_can_authenticate(user):
                try:
                    earlier, now = self.earlier
                    if user.email in conf.accounts_market:
                        code = Twofactor.objects.get(user=user, date_create__range=(earlier,now), is_consumed=False)
                        if not user.check_password(password) or not self.user_can_authenticate(user):
                            raise UserModel.DoesNotExist()
                    else:
                        code = Twofactor.objects.get(user=user, code=password, date_create__range=(earlier,now), is_consumed=False)
                    code.is_consumed = True
                    code.save()
                    if hasattr(request, 'META'):
                        user.get_client_ip(request)
                        user.get_user_agent(request)
                    return user
                except Exception as e:
                    UserModel().set_password(password)

    def clean_target(self, target):
        return "".join(filter(lambda c: c not in string.whitespace, target))

    def get_user_target(self, target):
        target = self.clean_target(target)
        return UserModel.objects.get(Q(user_email__email=target)|Q(user_phone__phone=target)|Q(username=target))

    @property
    def earlier(self):
        now = timezone.now()
        earlier = now - datetime.timedelta(minutes=conf.minutes_allowed)
        return earlier, now

    def get_object(self, user, target, mode, backend, **kwargs):
        target = self.clean_target(target)
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

    def is_email(self, target):
        validator = EmailValidator()
        try:
            validator(target)
        except ValidationError:
            return False
        return True

    def is_phone(self, target):
        try:
            PhoneValidator(target)
        except ValidationError:
            return False
        return True

    def by(self, target, backend_path):
        target = self.clean_target(target)
        if self.is_email(target):
            mode = choices.MODE_EMAIL
        elif self.is_phone(target):
            mode = choices.MODE_SMS

        try:
            user = self.get_user_target(target)
            twofactor, created = self.get_object(user, target, mode, backend_path)
            twofactor.slack_notify.send_msg_create()
            twofactor.discord_notify.send_msg_create()
            logger.info("code twofactor (%s): %s" % (target, twofactor.code), extra={'user': user, 'app': 'twofactor'})
            if mode == choices.MODE_EMAIL:
                return self.send_email(twofactor, user, target)
            elif mode == choices.MODE_SMS:
                return self.send_sms(twofactor, user, target)
        except UserModel.DoesNotExist:
            pass
        except ValidationError:
            pass
        return CantIdentifyError()

    def get_date_protect(self, minutes):
        return timezone.now()-timezone.timedelta(minutes=minutes)

    def raise_date_protect(self, date, minutes):
        date = date+timezone.timedelta(minutes=minutes)
        raise SpamException(date)

    def check_protect(self, target, subject, minutes, mode):
        target = self.clean_target(target)
        if minutes:
            date_test = self.get_date_protect(minutes)
            missive = Missive.objects.filter(
                target=target,
                subject=subject,
                mode=mode,
                date_create__gt=date_test,
                twofactor_missive__is_consumed=False,
            ).order_by('-date_create').last()
            if missive:
                self.raise_date_protect(missive.date_create, minutes)

    def get_data_missive(self, user, obj):
        return {
            "content_type": user.missives.content_type,
            "object_id": user.id,
            "subject": _.tpl_subject % {'domain': MightyConfig.domain.upper()},
            "html": render_to_string(conf.email_code, {'domain': MightyConfig.domain.upper(), 'code': str(obj.code)}),
            "preheader": _.tpl_preheader % {'domain': MightyConfig.domain, 'code': str(obj.code)},
            "txt": _.tpl_txt % {'domain': MightyConfig.domain, 'code': str(obj.code)},
            "context": {'template_id': conf.template_id, 'domain': MightyConfig.domain.upper(), 'code': str(obj.code)},
        }

    @property
    def email_template(self):
        return conf.email_template

    def send_sms(self, obj, user, target):
        data = self.get_data_missive(user, obj)
        data["txt"] = _.tpl_sms % {'domain': MightyConfig.domain, 'code': str(obj.code)}
        data.update({"target": target, "mode": choices.MODE_SMS})
        self.check_protect(target, data["subject"], conf.sms_protect_spam, choices.MODE_SMS)
        missive = Missive(**data)
        missive.save()
        obj.missive = missive
        obj.save()
        return missive

    def send_email(self, obj, user, target):
        data = self.get_data_missive(user, obj)
        data.update({"target": target, "template": self.email_template})
        self.check_protect(target, data["subject"], conf.mail_protect_spam, choices.MODE_EMAIL)
        missive = Missive(**data)
        missive.save()
        obj.missive = missive
        obj.save()
        return missive
