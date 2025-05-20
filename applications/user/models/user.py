import logging
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Q
from django.templatetags.static import static

from login import USERNAME_REGEX
from mighty.applications.address.models import AddressNoBase
from mighty.applications.messenger.decorators import AccessToMissive
from mighty.applications.nationality.fields import (
    nationality as fields_nationality,
)
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.user import (
    choices,
    fields,
    username_generator_v2,
    validators,
)
from mighty.applications.user import translates as _user
from mighty.applications.user.apps import UserConfig as conf
from mighty.applications.user.manager import UserManager
from mighty.decorators import AccessToRegisterTask
from mighty.models.base import Base
from mighty.models.image import Image

logger = logging.getLogger(__name__)

validate_trashmail = validators.validate_trashmail
validate_phone = validators.validate_phone


@AccessToRegisterTask()
@AccessToMissive()
class User(AbstractUser, Base, Image, AddressNoBase):
    enable_model_change_log = True
    search_fields = fields.search
    username = models.CharField(
        _user.username, max_length=254, unique=True, default='WILL_BE_GENERATED'
    )
    email = models.EmailField(
        _user.email,
        blank=True,
        null=True,
        db_index=True,
        validators=[validate_trashmail],
    )
    phone = models.CharField(
        _user.phone, blank=True, null=True, db_index=True, max_length=255
    )

    @staticmethod
    def validate_unique_email(email, pk=None):
        if not email:
            return email
        UserModel = get_user_model()
        qs = UserModel.objects.exclude(pk=pk) if pk else UserModel.objects
        if qs.filter(
            Q(email__iexact=email)
            | Q(**{
                conf.ForeignKey.email_related_name + '__email__iexact': email
            })
        ).exists():
            raise ValidationError(_user.error_email_already)
        return email

    @staticmethod
    def validate_unique_phone(phone, pk=None):
        if not phone:
            return phone
        UserModel = get_user_model()
        qs = UserModel.objects.exclude(pk=pk) if pk else UserModel.objects
        if qs.filter(
            Q(phone__iexact=phone) | Q(user_phone__phone__iexact=phone)
        ).exists():
            raise ValidationError(_user.error_phone_already)
        return phone

    method = models.CharField(
        _user.method,
        choices=choices.METHOD,
        default=choices.METHOD_FRONTEND,
        max_length=15,
    )
    method_backend = models.CharField(
        _user.method, max_length=255, blank=True, null=True
    )
    gender = fields.GenderField(blank=True, null=True)
    style = models.CharField(max_length=255, default='clear')
    channel = models.CharField(
        max_length=255, editable=False, blank=True, null=True
    )
    first_connection = models.DateTimeField(blank=True, null=True)
    sentry_replay = models.BooleanField(default=False)

    if conf.cgu:
        cgu = models.BooleanField(_user.cgu, default=False)
    if conf.cgv:
        cgv = models.BooleanField(_user.cgu, default=False)

    if conf.ForeignKey.optional:
        optional = models.ForeignKey(
            conf.ForeignKey.optional,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='optional_user',
        )
    if conf.ForeignKey.optional2:
        optional = models.ForeignKey(
            conf.ForeignKey.optional2,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='optional2_user',
        )
    if conf.ForeignKey.optional3:
        optional = models.ForeignKey(
            conf.ForeignKey.optional3,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='optional3_user',
        )
    if conf.ForeignKey.optional4:
        optional = models.ForeignKey(
            conf.ForeignKey.optional4,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='optional4_user',
        )
    if conf.ForeignKey.optional5:
        optional = models.ForeignKey(
            conf.ForeignKey.optional5,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='optional5_user',
        )

    # missives = GenericRelation("mighty.Missive")

    if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
        nationalities = models.ManyToManyField(
            conf.ForeignKey.nationalities, blank=True
        )
        language = models.ForeignKey(
            conf.ForeignKey.nationalities,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='language_user',
        )

        @property
        def language_pref(self):
            return self.language.alpha2.lower() if self.language else None

    if 'mighty.applications.tenant' in settings.INSTALLED_APPS:
        current_tenant = models.ForeignKey(
            TenantConfig.ForeignKey.tenant,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='current_tenant',
        )

        @property
        def all_nationalities(self):
            return {
                getattr(nat, fields_nationality[0]): {
                    field: getattr(nat, field)
                    for field in fields_nationality[1:]
                }
                for nat in self.nationalities.all()
            }

    class Meta(Base.Meta):
        db_table = 'auth_user'
        abstract = True
        verbose_name = _user.v_user
        verbose_name_plural = _user.vp_user
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
    def image_url(self):
        return self.image.url if self.image else static('img/avatar.svg')

    @property
    def user(self):
        return self

    @property
    def fullname(self):
        return (
            f'{self.first_name} {self.last_name}'
            if all([self.last_name, self.first_name])
            else ''
        )

    @property
    def logname(self):
        return f'{self.username}.{self.id}'

    @property
    def representation(self):
        if self.fullname:
            return self.fullname
        if self.username:
            return self.username
        return self.uid

    @property
    def is_first_login(self):
        return self.first_connection == self.last_login

    def __str__(self):
        if self.last_name and self.first_name:
            return self.fullname
        return getattr(self, self.USERNAME_FIELD)

    def has_perm(self, perm, obj=None):
        return super().has_perm(perm, obj=None)

    def get_client_ip(self, request):
        ip = (
            request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
            if request.META.get('HTTP_X_FORWARDED_FOR')
            else request.META.get('REMOTE_ADDR')
        )
        if ip is not None:
            internetprotocol = ContentType.objects.get(
                app_label='mighty', model='internetprotocol'
            ).model_class()
            _obj, _created = internetprotocol.objects.get_or_create(
                ip=ip, user=self
            )
            logger.info(f'connected from ip: {ip}', extra={'user': self})

    def get_user_agent(self, request):
        useragent = ContentType.objects.get(
            app_label='mighty', model='useragent'
        ).model_class()
        try:
            _obj, _created = useragent.objects.get_or_create(
                useragent=request.META['HTTP_USER_AGENT'], user=self
            )
        except useragent.MultipleObjectsReturned:
            usag = useragent.objects.filter(
                useragent=request.META['HTTP_USER_AGENT'], user=self
            )
            last = usag.last()
            usag.exclude(pk=last.pk).delete()
        logger.info(
            'usereagent: {}'.format(request.META['HTTP_USER_AGENT']),
            extra={'user': self},
        )

    def get_emails(self, flat=True):
        email_manager = getattr(self, conf.ForeignKey.email_related_name_attr)
        if flat:
            return email_manager.all().values_list('email', flat=True)
        return email_manager.all()

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
        return emails + phones + addresses

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
        logger.info('UserModel: pre_save')

        if self.username == 'WILL_BE_GENERATED' or not re.match(
            USERNAME_REGEX, self.username
        ):
            self.username = username_generator_v2(
                self.first_name, self.last_name, self.email
            )

        # Handle umique email and phone
        self.validate_unique_email(self.email, self.pk)
        self.validate_unique_phone(self.phone, self.pk)

        if self.email:
            self.email = self.email.lower()
        else:
            self.email = None

        if not self.phone:
            self.phone = None

        # Assign the first connection date
        if not self.first_connection and self.last_login:
            self.first_connection = self.last_login
