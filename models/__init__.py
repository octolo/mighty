from django.conf import settings
from django.db import  models
from mighty.applications.user.models import User, Email, Phone, InternetProtocol, UserAgent

if hasattr(settings, 'CHANNEL_LAYERS'):
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType
    from mighty.models.base import Base

    GROUP = 1
    USER = 0
    CHOICES_TYPE = (
        (GROUP, 'Group'),
        (USER, 'User')
    )
    class Channel(Base):
        channel_type = models.PositiveSmallIntegerField(choices=CHOICES_TYPE, default=USER)
        channel_name = models.CharField(max_length=255, null=True, blank=True)
        from_channel_name = models.CharField(max_length=255)
        from_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='chat_from_content_type')
        from_object_id = models.CharField(max_length=40)
        from_obj = GenericForeignKey('from_content_type', 'from_object_id')
        to_channel_name = models.CharField(max_length=255, null=True, blank=True)
        to_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_to_content_type')
        to_object_id = models.CharField(max_length=40, null=True, blank=True)
        to_obj = GenericForeignKey('to_content_type', 'to_object_id')

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

if 'mighty.applications.grapher' in settings.INSTALLED_APPS:
    from mighty.models.applications import grapher