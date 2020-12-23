from django.conf import settings
from django.db import  models
from django.utils.text import get_valid_filename

from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.models.keyword import Keyword
from mighty.applications.logger import EnableAccessLog, EnableChangeLog, models as models_logger
from mighty.functions import make_searchable

from django_ckeditor_5.fields import CKEditor5Field

###########################
# Models in mighty
###########################
class ConfigClient(Base):
    name = models.CharField(max_length=255, unique=True)
    url_name = models.CharField(max_length=255, null=True, blank=True, editable=False)
    config = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.url_name = get_valid_filename(make_searchable(self.name))
        super(ConfigClient, self).save(*args, **kwargs)

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

class News(Base, Keyword):
    keywords_fields = ['title',]
    title = models.CharField(max_length=255)
    news = CKEditor5Field(blank=True, null=True)
    date_news = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_news',]

    def __str__(self):
        return "%s - %s" % (str(self.date_news), self.title)

###########################
# Models apps mighty
###########################

# Logger
if 'mighty.applications.logger' in settings.INSTALLED_APPS:
    class Log(models_logger.Log): pass

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

# User
if 'mighty.applications.user' in settings.INSTALLED_APPS:
    from mighty.applications.user import models as models_user

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

# Twofactor
if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
    from mighty.applications.twofactor.models import Twofactor
    class Twofactor(Twofactor): pass

# Extend
if 'mighty.applications.extend' in settings.INSTALLED_APPS:
    from mighty.applications.extend import models as models_extend
    class Key(models_extend.Key): pass