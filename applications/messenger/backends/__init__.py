from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.core.mail.message import make_msgid

from mighty.functions import setting
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
        over_target = setting('MISSIVE_PHONE', False)
        self.missive.target = over_target if over_target else self.missive.target
        if setting('MISSIVE_SERVICE', False):
            pass
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        logger.info("send sms: %s" % self.message, extra=self.extra)
        return self.missive.status

    def send_email(self):
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target if over_target else self.missive.target
        if setting('MISSIVE_SERVICE', False):
            self.missive.msg_id = make_msgid()
            text_content = str(self.missive.txt)
            html_content = self.missive.html
            email = EmailMultiAlternatives(self.missive.subject, html_content, conf.sender_email, [self.missive.target], headers={'Message-Id': self.missive.msg_id})
            email.attach_alternative(html_content, "text/html")
            if self.missive.attachments:
                logs = []
                import os
                for document in self.missive.attachments:
                    email.attach(os.path.basename(document.name), document.read(), 'application/pdf')
                    logs.append(os.path.basename(document.name))
                self.missive.logs = logs
            email.send()
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        return self.missive.status

    def send_postal(self):
        if setting('MISSIVE_SERVICE', False):
            pass
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        return self.missive.status

    def check(self, missive):
        return True