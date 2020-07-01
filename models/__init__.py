from django.conf import settings
from django.db import  models
from mighty.fields import JSONField
from mighty.applications.user.models import User, Email, Phone, InternetProtocol, UserAgent

if hasattr(settings, 'CHANNEL_LAYERS'):
    from django.contrib.contenttypes.fields import GenericForeignKey
    from mighty.models.base import Base

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

if 'mighty.applications.logger' in settings.INSTALLED_APPS:
    from mighty.applications.logger.models import Log
    class Log(Log):
        pass

if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    from mighty.applications.nationality.models import Nationality
    class Nationality(Nationality):
        pass

if 'mighty.applications.user' in settings.INSTALLED_APPS:
    if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
        class User(User):
            nationalities = models.ManyToManyField(Nationality, blank=True)

    class Email(Email):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_email')

    class Phone(Phone):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_phone')

    class InternetProtocol(InternetProtocol):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_ip')

    class UserAgent(UserAgent):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_useragent')

    if 'mighty.applications.address' in settings.INSTALLED_APPS:
        from mighty.applications.address.models import Address
        class UserAddress(Address):
            user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_address')

    from mighty.applications.logger import EnableChangeLog
    from mighty.applications.logger.models import ChangeLog

    class UserLogModel(ChangeLog):
        object_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @EnableChangeLog(UserLogModel, ('logentry', 'password'))
    class ProxyUser(User):
        app_label = 'mighty'
        model_name = 'user'

        class Meta:
            app_label = 'auth'
            proxy = True
            verbose_name = User.Meta.verbose_name
            verbose_name_plural = User.Meta.verbose_name_plural

if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
    from mighty.applications.twofactor.models import Twofactor
    class Twofactor(Twofactor):
        class Meta:
            app_label = 'auth'

if 'mighty.applications.extend' in settings.INSTALLED_APPS:
    from mighty.applications.extend.models import Key, Extend
    class Key(Key):
        pass
        

if 'mighty.applications.grapher' in settings.INSTALLED_APPS:
    from mighty.models.applications import grapher