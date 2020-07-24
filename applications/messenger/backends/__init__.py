from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from mighty.models import Missive
from mighty.applications.messenger import choices
from mighty.functions import get_user_or_invitation_model
import datetime, logging

logger = logging.getLogger(__name__)
UserModel = get_user_or_invitation_model()

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