from django.db import models
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from mighty.models.base import Base
from mighty.applications.twofactor import translates as _
from mighty.applications.user import translates as _u
from mighty.functions import randomcode

UserModel = get_user_model()
STATUS_PREPARE = 'PREPARE'
STATUS_SENT = 'SENT'
STATUS_RECEIVED = 'RECEIVED'
STATUS_ERROR = 'ERROR'
MODE_EMAIL = 'EMAIL'
MODE_SMS = 'SMS'
CHOICES_MODE = ((MODE_EMAIL, _.MODE_EMAIL), (MODE_SMS, _.MODE_SMS),)
CHOICES_STATUS = ((STATUS_PREPARE, _.STATUS_PREPARE),(STATUS_SENT, _.STATUS_SENT),(STATUS_RECEIVED, _.STATUS_RECEIVED),(STATUS_ERROR, _.STATUS_ERROR),)

def generate_code(): return randomcode(5)

class Twofactor(Base):
    code = models.PositiveIntegerField(default=generate_code, db_index=True)
    is_consumed = models.BooleanField(default=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='code_user')
    email_or_phone = models.CharField(max_length=255)
    mode = models.CharField(choices=CHOICES_MODE, max_length=255)
    status = models.CharField(choices=CHOICES_STATUS, default=STATUS_PREPARE, max_length=100, editable=False, help_text='<a href="check"></a>')
    backend = models.CharField(max_length=255, editable=False)
    response = models.TextField(editable=False)
    subject = models.CharField(max_length=255)
    html = models.TextField()
    txt = models.TextField()

    class Meta(Base.Meta):
        abstract = True
        permissions = [('can_check', 'Check status'),]
        ordering = ['-date_create',]

    def __str__(self):
        return str(self.code)

    def get_backend(self):
        backend = import_string(self.backend)()
        return backend

    def check_status(self):
        backend = self.get_backend()
        return backend.check_email(self) if mode == MODE_EMAIL else backend.check_sms(self)

    def email(self):
        return self.user.email
    email.short_description = _u.email
    email.admin_order_field = 'user__email'

    def phone(self):
        return self.user.phone
    phone.short_description = _u.phone
    phone.admin_order_field = 'user__phone'