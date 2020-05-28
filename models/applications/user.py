from django.db import models
from django.conf import settings
from mighty.functions import setting
from mighty.applications.user.models import User, Email, Phone, InternetProtocol, UserAgent

if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
    from mighty.models.applications.nationality import Nationality
    class User(User):
        nationalities = models.ManyToManyField(Nationality, blank=True)
else:
    class User(User):
        pass

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
    class Meta:
        app_label = 'auth'
        proxy = True
        verbose_name = User.Meta.verbose_name
        verbose_name_plural = User.Meta.verbose_name_plural