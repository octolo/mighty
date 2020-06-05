from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.models.image import Image
from mighty.functions import test, get_logger

from mighty.applications.user.apps import UserConfig
from mighty.applications.user.manager import UserManager
from mighty.applications.user import translates as _, fields

from phonenumber_field.modelfields import PhoneNumberField
import uuid

logger = get_logger()
guardian = False
if 'guardian' in settings.INSTALLED_APPS:
    from guardian.core import ObjectPermissionChecker
    guardian = True

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
class User(AbstractUser, Base, Image):
    username = models.CharField(_.username, max_length=254, unique=True, blank=True, null=True)
    email = models.EmailField(_.email, unique=True)
    phone = PhoneNumberField(_.phone, blank=True, null=True, unique=True)
    method = models.CharField(_.method, choices=CHOICES_METHOD, default=METHOD_FRONTEND, max_length=15)
    method_backend = models.CharField(_.method, max_length=255, blank=True, null=True)
    gender = models.CharField(_.gender, max_length=1, choices=CHOICES_GENDER, blank=True, null=True)
    style = models.CharField(max_length=255, default="dark")

    class Meta(Base.Meta):
        db_table = 'auth_user'
        abstract = True
        verbose_name = _.v_user
        verbose_name_plural = _.vp_user
        ordering = ['last_name', 'first_name', 'email']

    USERNAME_FIELD = UserConfig.Field.username
    REQUIRED_FIELDS = UserConfig.Field.required
    objects = UserManager()

    @property
    def admin_list_url(self): return reverse('admin:auth_proxyuser_changelist')
    @property
    def admin_add_url(self): return reverse('admin:auth_proxyuser_add')
    @property
    def admin_change_url(self): return reverse('admin:auth_proxyuser_change', kwargs={"object_id": self.pk})
    @property
    def admin_disable_url(self): return reverse('admin:auth_proxyuser_disable', kwargs={"object_id": self.pk})
    @property
    def admin_enable_url(self): return reverse('admin:auth_proxyuser_enable', kwargs={"object_id": self.pk})
    @property
    def fullname(self): return "%s %s" % (self.last_name, self.first_name) if all([self.last_name, self.first_name]) else ''
    @property
    def logname(self): return '%s.%s' % (self.username, self.id)
    @property
    def representation(self):
        if self.fullname: return self.fullname
        if self.username: return self.username
        if self.email: return self.email
        return ''

    def __str__(self):
        if self.last_name and self.first_name:
            return self.fullname
        return getattr(self, self.USERNAME_FIELD)

    def has_perm(self, perm, obj=None):
        return ObjectPermissionChecker(user).has_perm(perm, obj) if guardian else super().has_perm(perm, obj=None)

    def get_client_ip(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')
        if ip is not None:
            internetprotocol = ContentType.objects.get(app_label='mighty', model='internetprotocol').model_class()
            obj, created = internetprotocol.objects.get_or_create(ip=ip, user=self)
            logger.info('connected from ip: %s',self, app="user")

    def get_user_agent(self, request):
        useragent = ContentType.objects.get(app_label='mighty', model='useragent').model_class()
        obj, created = useragent.objects.get_or_create(useragent=request.META['HTTP_USER_AGENT'], user=self)
        logger.info('usereagent: %s' % request.META['HTTP_USER_AGENT'], self, app="user")

    def set_search(self):
        self.search = ' '.join([getattr(self, field) for field in fields.searchs if hasattr(self, field) and test(getattr(self, field))])

    def gen_username(self):
        prefix = "".join([l for l in getattr(self, UserConfig.Field.username) if l.isalpha()])
        prefix = prefix[:3] if len(prefix) >= 3 else prefix
        exist = True
        while exist:
            username = '%s%s' % ('%s-' % prefix if prefix else '', str(uuid.uuid4())[:8])
            username = username.lower()
            try:
                type(self).objects.get(username=username)
            except type(self).DoesNotExist:
                exist = False
        return username

    def save(self, *args, **kwargs):
        if self.email is not None: self.email = self.email.lower()
        if self.username is not None: self.username = self.username.lower()
        else: self.username = self.gen_username()
        super(User, self).save(*args, **kwargs)

class Email(Base):
    email = models.EmailField(_.email, unique=True)
    default = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True

class Phone(Base):
    phone = PhoneNumberField(_.phone, unique=True)
    default = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True

class InternetProtocol(models.Model):
    ip = models.GenericIPAddressField(editable=False)

    class Meta(Base.Meta):
        abstract = True

class UserAgent(models.Model):
    useragent = models.CharField(max_length=255, editable=False)

    class Meta(Base.Meta):
        abstract = True