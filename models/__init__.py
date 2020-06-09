from django.conf import settings
from django.db import  models
from mighty.applications.user.models import User, Email, Phone, InternetProtocol, UserAgent

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