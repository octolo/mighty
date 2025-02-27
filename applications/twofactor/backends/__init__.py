import logging
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.validators import EmailValidator, ValidationError
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from mighty.applications.messenger import choices
from mighty.applications.twofactor import (
    CantIdentifyError,
    PhoneValidator,
    SpamException,
)
from mighty.applications.twofactor import translates as _
from mighty.applications.twofactor.apps import TwofactorConfig as conf
from mighty.applications.user.apps import UserConfig
from mighty.apps import MightyConfig
from mighty.functions import get_backends
from mighty.models import Missive, Twofactor

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class TwoFactorBackend(ModelBackend):
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

    def method_twofactor(self, user, target):
        email_manager = getattr(
            user, UserConfig.ForeignKey.email_related_name_attr
        )
        try:
            email_manager.get(email=target)
            return choices.MODE_EMAIL
        except email_manager.model.DoesNotExist:
            if (
                hasattr(user, 'email')
                and user.email == target
                and self.is_email(target)
            ):
                return choices.MODE_EMAIL

        try:
            user.user_phone.get(phone=target)
            return choices.MODE_SMS
        except email_manager.model.DoesNotExist:
            if (
                hasattr(user, 'phone')
                and user.phone == target
                and self.is_phone(target)
            ):
                return choices.MODE_SMS

        return False

    def Qfilters(self, target):
        return (
            Q(**{
                UserConfig.ForeignKey.email_related_name
                + '__email__iexact': target
            })
            | Q(user_phone__phone=target)
            | Q(username=target)
        )

    def clean_target(self, target):
        return ''.join(filter(lambda c: c not in string.whitespace, target))

    def get_user_target(self, target):
        target = self.clean_target(target)
        user = UserModel.objects.filter(self.Qfilters(target)).distinct()
        if len(user) == 1:
            return user[0], target
        raise UserModel.DoesNotExist

    def time_threshold(self, minutes):
        return timezone.now() - timezone.timedelta(minutes=minutes)

    def get_object(self, user, target, mode, backend, **kwargs):
        target = self.clean_target(target)
        time_threshold = self.time_threshold(conf.minutes_allowed)

        prepare = {
            'mode': mode,
            'email_or_phone': target,
            'user': user,
            'backend': backend,
            'date_create__gte': time_threshold,
            'is_consumed': False,
        }
        prepare.update(**kwargs)
        return Twofactor.objects.get_or_create(**prepare)

    def by(self, target, backend_path):
        try:
            user, target = self.get_user_target(target)
            mode = self.method_twofactor(user, target)
            twofactor, created = self.get_object(
                user, target, mode, backend_path
            )

            # FIXME: Need refacto with conf
            twofactor.slack_notify.send_msg_create()
            twofactor.discord_notify.send_msg_create()

            logger.info(
                'code twofactor (%s): %s' % (target, twofactor.code),
                extra={'user': user, 'app': 'twofactor'},
            )
            if mode == choices.MODE_EMAIL:
                return self.send_email(twofactor, user, target)
            if mode == choices.MODE_SMS:
                return self.send_sms(twofactor, user, target)
        except UserModel.DoesNotExist:
            pass
        except ValidationError:
            pass
        return CantIdentifyError()

    # def get_date_protect(self, minutes):
    # return timezone.now()-timezone.timedelta(minutes=minutes)

    def raise_date_protect(self, date, minutes):
        date = date + timezone.timedelta(minutes=minutes)
        raise SpamException(date)

    def check_protect(self, target, subject, minutes, mode):
        target = self.clean_target(target)
        if minutes:
            time_threshold = self.time_threshold(minutes)
            missive = (
                Missive.objects.filter(
                    target=target,
                    subject=subject,
                    mode=mode,
                    date_create__gte=time_threshold,
                    twofactor_missive__is_consumed=False,
                )
                .order_by('-date_create')
                .last()
            )
            # if missive:
            #    self.raise_date_protect(missive.date_create, minutes)

    def get_data_missive(self, user, obj):
        return {
            'content_type': user.missives.content_type,
            'object_id': user.id,
            'subject': _.tpl_subject % {'domain': MightyConfig.domain.upper()},
            'html': render_to_string(
                conf.email_code,
                {'domain': MightyConfig.domain.upper(), 'code': str(obj.code)},
            ),
            'preheader': _.tpl_preheader
            % {'domain': MightyConfig.domain, 'code': str(obj.code)},
            'txt': _.tpl_txt
            % {'domain': MightyConfig.domain, 'code': str(obj.code)},
            'context': {
                'template_id': conf.template_id,
                'domain': MightyConfig.domain.upper(),
                'code': str(obj.code),
            },
        }

    @property
    def email_template(self):
        return conf.email_template

    def get_backend(self, mode):
        backend = get_backends(
            service='twofactor_' + mode, only_string=True, silent_error=True
        )
        return backend[0] if backend else None

    def send_sms(self, obj, user, target):
        data = self.get_data_missive(user, obj)
        data['txt'] = _.tpl_sms % {
            'domain': MightyConfig.domain,
            'code': str(obj.code),
        }
        data.update({'target': target, 'mode': choices.MODE_SMS})
        missive = Missive(**data)
        missive.backend = self.get_backend('sms')
        missive.save()
        obj.missive = missive
        obj.save()
        return missive

    def send_email(self, obj, user, target):
        data = self.get_data_missive(user, obj)
        data.update({'target': target, 'template': self.email_template})
        self.check_protect(
            target, data['subject'], conf.mail_protect_spam, choices.MODE_EMAIL
        )
        missive = Missive(**data)
        missive.backend = self.get_backend('email')
        missive.save()
        obj.missive = missive
        obj.save()
        return missive

    # Old
    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     field_type = kwargs.get('field_type', None)
    #     if username is None:
    #         username = kwargs.get(UserModel.USERNAME_FIELD)
    #     if username is None or password is None:
    #         return
    #     try:
    #         if field_type == 'uid' and hasattr(UserModel, 'uid'):
    #             user = UserModel.objects.get(uid=username)
    #         else:
    #             user, username = self.get_user_target(username)
    #     except UserModel.DoesNotExist:
    #         UserModel().set_password(password)
    #     else:
    #         if self.user_can_authenticate(user):
    #             try:
    #                 earlier, now = self.earlier
    #                 if user.email in conf.accounts_market:
    #                     code = Twofactor.objects.get(user=user, date_create__range=(earlier,now), is_consumed=False)
    #                     if not user.check_password(password) or not self.user_can_authenticate(user):
    #                         raise UserModel.DoesNotExist()
    #                 else:
    #                     code = Twofactor.objects.get(user=user, code=password, date_create__range=(earlier,now), is_consumed=False)
    #                 code.is_consumed = True
    #                 code.save()
    #                 if hasattr(request, 'META'):
    #                     user.get_client_ip(request)
    #                     user.get_user_agent(request)
    #                 return user
    #             except Exception as e:
    #                 UserModel().set_password(password)

    # New

    # New
    def authenticate(self, request, username=None, password=None, **kwargs):
        field_type = kwargs.get('field_type')

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return None

        try:
            user = None
            if field_type == 'uid' and hasattr(UserModel, 'uid'):
                user = UserModel.objects.get(uid=username)
            else:
                user, username = self.get_user_target(username)

            if not user:
                return None

            if self.user_can_authenticate(user):
                return self.handle_two_factor_authentication(
                    user, password, request
                )

            if hasattr(request, 'META'):
                user.get_client_ip(request)
                user.get_user_agent(request)

        except UserModel.DoesNotExist:
            return None

    def handle_two_factor_authentication(self, user, password, request):
        try:
            time_threshold = self.time_threshold(conf.minutes_allowed)
            if user.email in conf.accounts_market:
                code = Twofactor.objects.get(
                    user=user,
                    date_create__gte=time_threshold,
                    is_consumed=False,
                )
                valid_password = user.check_password(password)
            else:
                code = Twofactor.objects.get(
                    user=user,
                    code=password,
                    date_create__gte=time_threshold,
                    is_consumed=False,
                )
                valid_password = True

            if not valid_password or not self.user_can_authenticate(user):
                return None

            code.is_consumed = True
            code.save()

            return user
        except Twofactor.DoesNotExist:
            return None
        except Exception as e:
            logger.error(
                'Two-factor authentication error: %s' % str(e),
                extra={'user': user.id},
            )
            return None
