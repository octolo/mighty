from django.db import models
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from mighty.models.base import Base
from mighty.applications.twofactor import translates as _
from mighty.applications.twofactor.apps import TwofactorConfig as conf
from mighty.applications.user import translates as _u
from mighty.functions import randomcode
from mighty.applications.messenger import choices

UserModel = get_user_model()

def generate_code(): 
    return randomcode(conf.code_size)

class Twofactor(Base):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='twofactor_user')
    missive = models.ForeignKey('mighty.Missive', on_delete=models.SET_NULL, null=True, related_name='twofactor_missive')
    email_or_phone = models.CharField(max_length=255)
    code = models.PositiveIntegerField(default=generate_code, db_index=True)
    is_consumed = models.BooleanField(default=False)
    mode = models.CharField(choices=choices.MODE, max_length=255)
    backend = models.CharField(max_length=255, editable=False)

    class Meta(Base.Meta):
        abstract = True
        permissions = [('can_check', 'Check status'),]
        ordering = ['-date_create',]

    def __str__(self):
        return str(self.code)

    def get_backend(self):
        backend = import_string(self.backend)()
        return backend

    @property
    def slack_notify(self):
        from mighty.applications.twofactor.notify.slack import SlackTwoFactor
        return SlackTwoFactor(self)

    @property
    def discord_notify(self):
        from mighty.applications.twofactor.notify.discord import DiscordTwoFactor
        return DiscordTwoFactor(self)
        