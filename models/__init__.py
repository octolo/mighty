from django.conf import settings
from django.db import  models
from django.utils.text import get_valid_filename
from django.contrib.contenttypes.models import ContentType

from mighty.apps import MightyConfig as conf
from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.models.news import News
from mighty.models.config import Config
from mighty.models.backend import Backend
from mighty.models.reporting import Reporting
from mighty.models.registertask import RegisterTask
from mighty.applications.logger import EnableAccessLog, EnableChangeLog, models as models_logger


###########################
# Models in mighty
###########################
class Backend(Backend): pass
class Reporting(Reporting): pass
class RegisterTask(RegisterTask): pass

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

class TemplateVariable(Base):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    template = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="template_variable")
    hidden = models.BooleanField(default=False)

    class Meta(Base.Meta):
        unique_together = ("name", "content_type")

    @property
    def var_prefix(self): return self.content_type.model_class().eve_variable_prefix+"eve_tv."
    @property
    def var_name(self): return self.var_prefix+self.name
    @property
    def json_object(self): return { "var": self.var_name, "desc": self.description }

    def pre_save(self):
        if not self.description:
            self.description = self.name

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
                'state': 'connected'
            }
            self.save()

        def disconnect_user(self, _id, close_code='disconnected'):
            self.objs[_id]['state'] = close_code
            self.save()

        def historize(self, _id, event, datas):
            if _id not in self.history: self.history[_id] = []
            self.history[_id].append({event: datas})
            self.save()

        def save(self, *args, **kwargs):
            if not self.from_id: self.from_id = next(iter(self.objs))
            super(Channel, self).save(*args, **kwargs)


###########################
# Models apps mighty
###########################

# Logger
if 'mighty.applications.logger' in settings.INSTALLED_APPS:
    class Log(models_logger.Log): pass
    class ModelChangeLog(models_logger.ModelChangeLog): pass

# Nationality
if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    from mighty.applications.nationality import models as models_nationality
    class Nationality(models_nationality.Nationality): pass
    class Translator(models_nationality.Translator): pass
    class TranslateDict(models_nationality.TranslateDict): pass

# Messenger
if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
    from mighty.applications.messenger import models as models_messenger
    class Missive(models_messenger.Missive): pass
    class Notification(models_messenger.Notification): pass
    class Template(models_messenger.Template): pass

# User
if 'mighty.applications.user' in settings.INSTALLED_APPS:
    from mighty.applications.user import models as models_user
    from mighty.applications.user.apps import UserConfig as user_conf
    class UserAccessLogModel(models_user.UserAccessLogModel): pass
    class UserChangeLogModel(models_user.UserChangeLogModel): pass
    @EnableAccessLog(UserAccessLogModel)
    @EnableChangeLog(UserChangeLogModel, ('logentry', 'password', 'tenant'))
    class User(models_user.User): pass
    class UserEmail(models_user.UserEmail): pass
    class UserPhone(models_user.UserPhone): pass
    class InternetProtocol(models_user.InternetProtocol): pass
    class UserAgent(models_user.UserAgent): pass
    class UserAddress(models_user.UserAddress): pass
    class Invitation(models_user.Invitation): pass
    if user_conf.protect_trashmail:
        class Trashmail(models_user.Trashmail): pass

# Data protect
if 'mighty.applications.dataprotect' in settings.INSTALLED_APPS:
    from mighty.applications.dataprotect import models as models_dataprotect
    class ServiceData(models_dataprotect.ServiceData): pass
    class UserDataProtect(models_dataprotect.UserDataProtect): pass

# Twofactor
if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
    from mighty.applications.twofactor.models import Twofactor
    class Twofactor(Twofactor): pass

# Extend
if 'mighty.applications.extend' in settings.INSTALLED_APPS:
    from mighty.applications.extend import models as models_extend
    class Key(models_extend.Key): pass

# Shop
if 'mighty.applications.shop' in settings.INSTALLED_APPS:
    from mighty.applications.shop import models as models_shop
    class ShopService(models_shop.ShopService): pass
    class Offer(models_shop.Offer): pass
    class Subscription(models_shop.Subscription): pass
    class Discount(models_shop.Discount): pass
    class ShopItem(models_shop.ShopItem): pass
    class Bill(models_shop.Bill): pass
    class PaymentMethod(models_shop.PaymentMethod): pass
    class SubscriptionRequest(models_shop.SubscriptionRequest): pass

if conf.enable_mimetype:
    from mighty.models.filesystem import MimeType
    class MimeType(MimeType): pass
