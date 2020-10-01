from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from mighty.models import Missive
from mighty.applications.messenger import choices
from mighty.applications.messenger.apps import MessengerConfig as conf
import datetime, logging


logger = logging.getLogger(__name__)

class MissiveBackend:
    def __init__(self, missive, *args, **kwargs):
        self.missive = missive

    @property
    def extra(self):
        return {'user': self.missive.content_object, 'app': 'messenger'}

    @property
    def message(self):
        return self.missive.txt if self.missive.txt else self.missive.html

    def send(self):
        return getattr(self, 'send_%s' % self.missive.mode.lower())()

    def send_sms(self):
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        logger.info("send sms: %s" % self.message, extra=self.extra)
        return self.missive.status

    def send_email(self):
        if conf.enable.email:
            send_mail(
                subject=self.missive.subject,
                message=self.missive.txt,
                html_message=self.missive.html,
                from_email=conf.sender_email,
                recipient_list=[self.missive.target],
                fail_silently=False
            )
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        logger.info("send email: %s" % self.message, extra=self.extra)
        return self.missive.status

    def send_postal(self):
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        logger.info("send postal: %s" % self.message, extra=self.extra)
        return self.missive.status

    def check(self, missive):
        return True