from django.conf import settings
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.template import Context
from django.core.mail import send_mail

from mighty.applications.twofactor.backends import TwoFactorBackend

conf = settings.TWOFACTOR

class TwoFactorBackend(TwoFactorBackend):
    def send_sms(self, user, backend_path):
        twofactor = super().send_sms(user, backend_path)
        send_mail(
            '%s - Auth Code' % conf['site'],
            twofactor.txt,
            conf['sender_mail'],
            [user.email],
            fail_silently=False
        )
        return twofactor

    def send_email(self, user, backend_path):
        BOARDDATA_MAIL_FROM = "balos@boarddata.fr"
        send_mail(
            '%s - Auth Code' % conf['site'],
            twofactor.txt,
            conf['sender_mail'],
            [user.email],
            fail_silently=False
        )
        twofactor = super().send_email(user, backend_path)
        return twofactor
