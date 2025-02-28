
import logging
import re

from django.db import models
from django.db.models import Index, Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from mighty.applications.user import translates as _user
from mighty.applications.user.apps import UserConfig as conf
from mighty.functions import masking_phone
from mighty.models import Base

logger = logging.getLogger(__name__)

# Django-allauth utils
from allauth.account.utils import user_field


def user_phone(user, *args, commit=False):
    return user_field(user, 'phone', *args, commit=commit)


# Django-allauth implementation
class UserPhoneManager(models.Manager):
    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None


# FIXME: This model will be changed to Phones soon, as a copy from EmailAddress from Django Allauth, with a real phonenumbers field
class UserPhone(models.Model):
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_phone')
    phone = models.CharField(_user.phone, unique=True, max_length=255)
    search_fields = ('phone',)
    # Until we create a model like Django Allauth
    primary = models.BooleanField(verbose_name=_('primary'), default=False)
    verified = models.BooleanField(verbose_name=_('verified'), default=False)

    objects = UserPhoneManager()

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _user.phone
        unique_together = [('user', 'phone')]
        constraints = [
            UniqueConstraint(
                fields=['phone'],
                name='unique_verified_phone_number',
                condition=Q(verified=True),
            )
        ]
        indexes = [Index(('phone'), name='phone_idx')]

    def __str__(self):
        return self.phone

    def clean_phone(self):
        self.phone = re.sub(r'[^+0-9]+', '', self.phone)

    # Django-allauth implementation
    def can_set_verified(self):

        if self.verified:
            return True
        # conflict = False
        # if app_settings.UNIQUE_EMAIL:
        conflict = (
            type(self).objects.exclude(pk=self.pk)
            .filter(verified=True, phone__iexact=self.phone)
            .exists()
        )
        logger.info(f'can_set_verified: {conflict}')
        return not conflict

    def set_verified(self, commit=True):
        logger.info('can_set_verified')
        if self.verified:
            return True
        if self.can_set_verified():
            logger.info('can_set_verified: True')
            self.verified = True
            if commit:
                self.save(update_fields=['verified'])
        return self.verified

    def set_as_primary(self, conditional=False):
        """Marks the email address as primary. In case of `conditional`, it is
        only marked as primary if there is no other primary email address set.
        """
        # from allauth.account.utils import user_email

        old_primary = type(self).objects.get_primary(self.user)
        logger.info(f'set_as_primary: {old_primary}')
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        user_phone(self.user, self.phone, commit=True)
        return True

    def pre_save(self):
        self.clean_phone()
        super().pre_save()

    @property
    def masking(self):
        return masking_phone(self.phone)
