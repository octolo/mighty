from django.apps import apps
from django.conf import settings
from django.db import models

from mighty.applications.logger import models as models_logger
from mighty.apps import MightyConfig as conf
from mighty.fields import JSONField
from mighty.models.backend import Backend
from mighty.models.base import Base
from mighty.models.config import Config
from mighty.models.news import News as News
from mighty.models.registertask import RegisterTask, RegisterTaskSubscription
from mighty.models.reporting import Reporting
from mighty.models.variable import TemplateVariable


###########################
# Models in mighty
###########################
class Backend(Backend):
    pass


class Reporting(Reporting):
    pass


class RegisterTask(RegisterTask):
    pass


class RegisterTaskSubscription(RegisterTaskSubscription):
    pass


class TemplateVariable(TemplateVariable):
    pass


class ConfigClient(Config):
    config = JSONField(null=True, blank=True)


class ConfigSimple(Config):
    configchar = models.CharField(max_length=255, null=True, blank=True)
    configbool = models.BooleanField(default=False)
    is_boolean = models.BooleanField(default=False)

    @property
    def config(self):
        return self.configbool if self.is_boolean else self.configchar

    class Meta(Base.Meta):
        ordering = ('date_create', 'name')


if hasattr(settings, 'CHANNEL_LAYERS'):

    class Channel(Base):
        channel_name = models.CharField(max_length=255, null=True, blank=True)
        channel_type = models.CharField(max_length=255)
        from_id = models.CharField(max_length=40)
        objs = JSONField(default=dict)
        history = JSONField(default=dict)

        def connect_user(self, channel_name, obj, _id):
            self.objs[_id] = {
                'model': obj._meta.model_name,
                'label': obj._meta.app_label,
                'channel_name': channel_name,
                'state': 'connected',
            }
            self.save()

        def disconnect_user(self, _id, close_code='disconnected'):
            self.objs[_id]['state'] = close_code
            self.save()

        def historize(self, _id, event, datas):
            if _id not in self.history:
                self.history[_id] = []
            self.history[_id].append({event: datas})
            self.save()

        def save(self, *args, **kwargs):
            if not self.from_id:
                self.from_id = next(iter(self.objs))
            super().save(*args, **kwargs)


###########################
# Models apps mighty
###########################

# Logger
if 'mighty.applications.logger' in settings.INSTALLED_APPS:

    class Log(models_logger.Log):
        pass

    class ModelChangeLog(models_logger.ModelChangeLog):
        pass


# Nationality
if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    from mighty.applications.nationality import models as models_nationality

    class Nationality(models_nationality.Nationality):
        pass

    class Translator(models_nationality.Translator):
        pass

    class TranslateDict(models_nationality.TranslateDict):
        pass


# Messenger
if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
    from mighty.applications.messenger import models as models_messenger

    class Missive(models_messenger.Missive):
        pass

    class Notification(models_messenger.Notification):
        pass

    class Template(models_messenger.Template):
        pass


# User
if 'mighty.applications.user' in settings.INSTALLED_APPS:
    from mighty.applications.user import models as models_user
    from mighty.applications.user.apps import UserConfig as user_conf

    class User(models_user.User):
        pass

    if not apps.is_installed('allauth'):

        class UserEmail(models_user.UserEmail):
            pass

    class UserPhone(models_user.UserPhone):
        pass

    class InternetProtocol(models_user.InternetProtocol):
        pass

    class UserAgent(models_user.UserAgent):
        pass

    class UserAddress(models_user.UserAddress):
        pass

    if user_conf.protect_trashmail:

        class Trashmail(models_user.Trashmail):
            pass

    # Draft
    class MergeableAccount(models_user.MergeableAccount):
        pass


# Data protect
if 'mighty.applications.dataprotect' in settings.INSTALLED_APPS:
    from mighty.applications.dataprotect import models as models_dataprotect

    class ServiceData(models_dataprotect.ServiceData):
        pass

    class UserDataProtect(models_dataprotect.UserDataProtect):
        pass


# Twofactor
if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
    from mighty.applications.twofactor.models import Twofactor

    class Twofactor(Twofactor):
        pass


# Extend
if 'mighty.applications.extend' in settings.INSTALLED_APPS:
    from mighty.applications.extend import models as models_extend

    class Key(models_extend.Key):
        pass


if conf.enable_mimetype:
    from mighty.models.filesystem import MimeType

    class MimeType(MimeType):
        pass
