from django.db import models
from django.contrib.auth.models import AbstractUser

from mighty.models import JSONField
from mighty.models.base import Base
from mighty.models.uid import Uid
from mighty.models.disable import Disable
from mighty.models.alert import Alert
from mighty.models.image import Image
from mighty.models.search import Search
from mighty.functions import test, logger

from mighty.applications.user.apps import UserConfig
from mighty.applications.user.manager import UserManager
from mighty.applications.user import translates as _, fields

from phonenumber_field.modelfields import PhoneNumberField

METHOD_CREATESU = 'CREATESUPERUSER'
METHOD_BACKEND = 'BACKEND'
METHOD_FRONTEND = 'FRONTEND'
METHOD_IMPORT = 'IMPORT'
GENDER_MAN = 'M'
GENDER_WOMAN = 'W'
CHOICES_METHOD = (
    (METHOD_CREATESU, _.METHOD_CREATESU),
    (METHOD_BACKEND, _.METHOD_BACKEND),
    (METHOD_FRONTEND, _.METHOD_FRONTEND),
    (METHOD_IMPORT, _.METHOD_IMPORT))
CHOICES_GENDER = ((GENDER_MAN, _.GENDER_MAN), (GENDER_WOMAN, _.GENDER_WOMAN))
class User(AbstractUser, Uid, Base, Disable, Alert, Image, Search):
    username = models.CharField(_.username, max_length=254, validators=[AbstractUser.username_validator], unique=True, blank=True, null=True)
    email = models.EmailField(_.email, unique=True)
    phone = PhoneNumberField(_.phone, blank=True, null=True)
    method = models.CharField(_.method, choices=CHOICES_METHOD, default=METHOD_FRONTEND, max_length=15)
    method_backend = models.CharField(_.method, max_length=255, blank=True, null=True)
    gender = models.CharField(_.gender, max_length=1, choices=CHOICES_GENDER, blank=True, null=True)

    class Meta(Disable.Meta):
        abstract = True
        verbose_name = _.v_user
        verbose_name_plural = _.vp_user
        ordering = ['last_name', 'first_name', 'email']

    USERNAME_FIELD = UserConfig.Field.username
    REQUIRED_FIELDS = UserConfig.Field.required
    objects = UserManager()

    def __str__(self):
        return getattr(self, self.USERNAME_FIELD)

    def get_client_ip(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')
        if ip is not None:
            obj, created = InternetProtocol.objects.get_or_create(ip=ip, user=self)
            logger('test', 'info', 'connected from ip: %s' % ip, user=self)

    def set_search(self):
        self.search = ' '.join([getattr(self, field) for field in fields.searchs if hasattr(self, field) and test(getattr(self, field))])

    def save(self, *args, **kwargs):
        if self.email is not None: self.email = self.email.lower()
        if self.username is not None: self.username = self.username.lower()
        super().save(*args, **kwargs)

class Email(Base, Disable):
    email = models.EmailField(_.email, unique=True)
    default = models.BooleanField(default=False)

    class Meta(Disable.Meta):
        abstract = True

class Phone(Base, Disable):
    phone = PhoneNumberField(_.phone, unique=True)
    default = models.BooleanField(default=False)

    class Meta(Disable.Meta):
        abstract = True

#class Address(Base, Disable):
#    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_address')

class InternetProtocol(Base, Disable):
    ip = models.GenericIPAddressField(editable=False)

    class Meta(Disable.Meta):
        abstract = True