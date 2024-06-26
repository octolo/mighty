from django.apps import apps
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext_lazy as _django

from mighty.decorators import AccessToRegisterTask
from mighty.models.base import Base
from mighty.models.image import Image
from mighty.functions import masking_email, masking_phone
from mighty.applications.logger.models import ChangeLog
from mighty.applications.address.models import Address, AddressNoBase
from mighty.applications.address import fields as address_fields
from mighty.applications.user.apps import UserConfig as conf
from mighty.applications.user.manager import UserManager
from mighty.applications.user import translates as _, fields, choices, validators
from mighty.applications.user import username_generator_v2
from mighty.applications.messenger.decorators import AccessToMissive
from mighty.applications.nationality.fields import nationality as fields_nationality
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.user.apps import UserConfig

from login import USERNAME_REGEX

# from phonenumber_field.modelfields import PhoneNumberField
import logging, re

logger = logging.getLogger(__name__)

validate_phone = validators.validate_phone
validate_trashmail = validators.validate_trashmail

class Data(models.Model):
    default = models.BooleanField(verbose_name=_django("primary"), default=False)

    class Meta:
        abstract = True

    def many_or_default(self):
        qs = self.qs_not_self.filter(user=self.user, default=True)
        self.default = self.default if len(qs) else True

    def set_default_data(self):
        data = self.search_fields[0]
        udata = getattr(self.user, data)
        if (self.default or not udata) and udata != getattr(self, data):
            setattr(self.user, data, getattr(self, data))
            self.user.save()

    def pre_save(self):
        self.many_or_default()

    def post_save(self):
        self.set_default_data()

class UserEmail(Data, Base):
    enable_model_change_log = True
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_email')
    email = models.EmailField(_.email, unique=True, validators=[validate_trashmail])
    search_fields = ('email',)

    def __str__(self):
        return "%s - %s" % (str(self.user), self.email)

    class Meta(Base.Meta):
        abstract = True

    def pre_save(self):
        self.email = self.email.lower()
        super().pre_save()

    @property
    def masking(self):
        return masking_email(self.email)

#FIXME: This model will be changed to Phones soon, as a copy from EmailAddress from Django Allauth, with a real phonenumbers field
class UserPhone(Data, Base):
    enable_model_change_log = True
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_phone')
    phone = models.CharField(_.phone, unique=True, max_length=255)
    search_fields = ('phone',)
    # Until we create a model like Django Allauth
    verified = models.BooleanField(verbose_name=_django("verified"), default=False)

    def clean_phone(self):
        self.phone = re.sub('[^+0-9]+', '', self.phone)

    def __str__(self):
        return self.phone

    def pre_save(self):
        self.clean_phone()
        super().pre_save()

    class Meta(Base.Meta):
        abstract = True

    @property
    def masking(self):
        return masking_phone(self.phone)

class UserAddress(Data, Address):
    enable_model_change_log = True
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_address')
    enable_clean_fields = True

    def __str__(self):
        return "%s - %s" % (str(self.user), self.representation)

    class Meta(Base.Meta):
        abstract = True

    @property
    def masking(self):
        return "**"

    def set_default_data(self):
        data = "raw"
        udata = getattr(self.user, data)
        if (self.default or not udata) and udata != getattr(self, data):
            for field in address_fields:
                setattr(self.user, field, getattr(self, field))
            self.user.save()

class InternetProtocol(models.Model):
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_ip')
    ip = models.GenericIPAddressField(editable=False)

    class Meta(Base.Meta):
        abstract = True

class UserAgent(models.Model):
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_useragent')
    useragent = models.CharField(max_length=255, editable=False)

    class Meta(Base.Meta):
        abstract = True

class UserAccessLogModel(ChangeLog):
    object_id = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_accesslog')

    class Meta:
        abstract = True

class UserChangeLogModel(ChangeLog):
    object_id = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_changelog')

    class Meta:
        abstract = True


@AccessToRegisterTask()
@AccessToMissive()
class User(AbstractUser, Base, Image, AddressNoBase):
    enable_model_change_log = True
    search_fields = fields.search
    username = models.CharField(_.username, max_length=254, unique=True, default="WILL_BE_GENERATED")
    email = models.EmailField(_.email, blank=True, null=True, db_index=True, validators=[validate_trashmail])
    phone = models.CharField(_.phone, blank=True, null=True, db_index=True, max_length=255)

    @staticmethod
    def validate_unique_email(email, pk=None):
        if not email: return email
        UserModel = get_user_model()
        qs = UserModel.objects.exclude(pk=pk) if pk else UserModel.objects
        if qs.filter(Q(email__iexact=email) | Q(**{UserConfig.ForeignKey.email_related_name + "__email__iexact": email})).exists():
            raise ValidationError(_.error_email_already)
        return email

    @staticmethod
    def validate_unique_phone(phone, pk=None):
        if not phone: return phone
        UserModel = get_user_model()
        qs = UserModel.objects.exclude(pk=pk) if pk else UserModel.objects
        if qs.filter(Q(phone__iexact=phone) | Q(user_phone__phone__iexact=phone)).exists():
            raise ValidationError(_.error_phone_already)
        return phone

    method = models.CharField(_.method, choices=choices.METHOD, default=choices.METHOD_FRONTEND, max_length=15)
    method_backend = models.CharField(_.method, max_length=255, blank=True, null=True)
    gender = fields.GenderField(blank=True, null=True)
    style = models.CharField(max_length=255, default="clear")
    channel = models.CharField(max_length=255, editable=False, blank=True, null=True)
    first_connection = models.DateTimeField(blank=True, null=True)
    sentry_replay = models.BooleanField(default=False)

    if conf.cgu:
        cgu = models.BooleanField(_.cgu, default=False)
    if conf.cgv:
        cgv = models.BooleanField(_.cgu, default=False)

    if conf.ForeignKey.optional:
        optional = models.ForeignKey(conf.ForeignKey.optional, on_delete=models.SET_NULL, blank=True, null=True, related_name='optional_user')
    if conf.ForeignKey.optional2:
        optional = models.ForeignKey(conf.ForeignKey.optional2, on_delete=models.SET_NULL, blank=True, null=True, related_name='optional2_user')
    if conf.ForeignKey.optional3:
        optional = models.ForeignKey(conf.ForeignKey.optional3, on_delete=models.SET_NULL, blank=True, null=True, related_name='optional3_user')
    if conf.ForeignKey.optional4:
        optional = models.ForeignKey(conf.ForeignKey.optional4, on_delete=models.SET_NULL, blank=True, null=True, related_name='optional4_user')
    if conf.ForeignKey.optional5:
        optional = models.ForeignKey(conf.ForeignKey.optional5, on_delete=models.SET_NULL, blank=True, null=True, related_name='optional5_user')

    #missives = GenericRelation("mighty.Missive")

    if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
        nationalities = models.ManyToManyField(conf.ForeignKey.nationalities, blank=True)
        language = models.ForeignKey(conf.ForeignKey.nationalities, on_delete=models.SET_NULL, blank=True, null=True, related_name="language_user")

        @property
        def language_pref(self):
            return self.language.alpha2.lower() if self.language else None

    if 'mighty.applications.tenant' in settings.INSTALLED_APPS:
        current_tenant = models.ForeignKey(TenantConfig.ForeignKey.tenant, on_delete=models.SET_NULL, blank=True, null=True, related_name='current_tenant')

        @property
        def all_nationalities(self):
            return {
                getattr(nat, fields_nationality[0]): {field: getattr(nat, field) for field in fields_nationality[1:]}
                for nat in self.nationalities.all()}

    class Meta(Base.Meta):
        db_table = 'auth_user'
        abstract = True
        verbose_name = _.v_user
        verbose_name_plural = _.vp_user
        ordering = ['last_name', 'first_name', 'email']

    USERNAME_FIELD = conf.Field.username
    REQUIRED_FIELDS = conf.Field.required
    objects = UserManager()

    def disable(self):
        self.is_disable = True
        self.is_active = False
        self.save()

    def enable(self):
        self.is_disable = False
        self.is_active = True
        self.save()

    @property
    def image_url(self): return self.image.url if self.image else static("img/avatar.svg")

    @property
    def user(self):
        return self

    @property
    def fullname(self):
        return "%s %s" % (self.first_name, self.last_name) if all([self.last_name, self.first_name]) else ''

    @property
    def logname(self):
        return '%s.%s' % (self.username, self.id)

    @property
    def representation(self):
        if self.fullname: return self.fullname
        elif self.username: return self.username
        return self.uid

    @property
    def is_first_login(self):
        return (self.first_connection == self.last_login)

    def __str__(self):
        if self.last_name and self.first_name:
            return self.fullname
        return getattr(self, self.USERNAME_FIELD)

    def has_perm(self, perm, obj=None):
        return super().has_perm(perm, obj=None)

    def get_client_ip(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')
        if ip is not None:
            internetprotocol = ContentType.objects.get(app_label='mighty', model='internetprotocol').model_class()
            obj, created = internetprotocol.objects.get_or_create(ip=ip, user=self)
            logger.info('connected from ip: %s' % ip, extra={'user': self})

    def get_user_agent(self, request):
        useragent = ContentType.objects.get(app_label='mighty', model='useragent').model_class()
        obj, created = useragent.objects.get_or_create(useragent=request.META['HTTP_USER_AGENT'], user=self)
        logger.info('usereagent: %s' % request.META['HTTP_USER_AGENT'], extra={'user': self})

    def get_emails(self, flat=True):
        email_manager = getattr(self, UserConfig.ForeignKey.email_related_name_attr)
        if flat:
            return email_manager.all().values_list('email', flat=True)
        return email_manager.all()

    def in_emails(self):
        if not self.email:
            return
        email_manager = getattr(self, UserConfig.ForeignKey.email_related_name_attr)
        flag_name = 'primary' if apps.is_installed('allauth') else 'default'
        updated = email_manager.filter(email=self.email).update(**{flag_name: True})
        if not updated:
            email_manager.create(email=self.email, **{flag_name: True})
        email_manager.exclude(email=self.email).update(**{flag_name: False})

    def get_phones(self, flat=True):
        if flat:
            return self.user_phone.all().values_list('phone', flat=True)
        return self.user_phone.all()

    def in_phones(self):
        if self.phone:
            try:
                self.user_phone.get(phone=self.phone)
            except ObjectDoesNotExist:
                self.user_phone.create(phone=self.phone, default=True)
            self.user_phone.exclude(phone=self.phone).update(default=False)

    @property
    def user_data(self):
        emails = tuple(self.get_emails())
        phones = tuple(self.get_phones())
        addresses = tuple(self.get_addresses())
        return emails+phones+addresses


    def get_addresses(self, flat=True):
        if flat:
            return self.user_address.all().values_list('raw', flat=True)
        return self.user_address.all()

    def in_address(self):
        pass

    @property
    def slack_notify(self):
        from mighty.applications.user.notify.slack import SlackUser
        return SlackUser(self)

    def pre_save(self):
        # Old
        # if self.email is not None: self.email = self.email.lower()
        # self.username = self.username.lower() if self.username is not None else self.gen_username()
        # if not self.first_connection and self.last_login:
        #     self.first_connection = self.last_login

        if self.username == "WILL_BE_GENERATED" or not re.match(USERNAME_REGEX, self.username):
            self.username = username_generator_v2(self.first_name, self.last_name, self.email)

        # Handle umique email and phone
        self.validate_unique_email(self.email, self.pk)
        self.validate_unique_phone(self.phone, self.pk)

        if self.email:
            self.email = self.email.lower()

        # Assign the first connection date
        if not self.first_connection and self.last_login:
            self.first_connection = self.last_login

    def post_save(self, *args, **kwargs):
        self.in_emails()
        self.in_phones()

class Trashmail(Base):
    domain = models.CharField(max_length=255)

    class Meta(Base.Meta):
        abstract = True

    def __str__(self):
        return "@" + self.domain

# Draft
class MergeableAccount(Base):
    primary_user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='primary_user')
    secondary_user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='mergeable_user')
    reason = models.CharField(max_length=255)
    is_merged = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True

    def __str__(self):
        return f"{self.primary_user} - {self.secondary_user}"
