import re

from django.conf import settings
from django.core.exceptions import ValidationError
from schwifty import BIC, IBAN

from mighty.applications.shop.apps import ShopConfig, sepas_test


class IbanModel:
    @property
    def readable_iban(self):
        return ' '.join([self.iban[i:i + 4] for i in range(0, len(self.iban), 4)])

    @property
    def str_iban(self):
        return '%s/%s' % (self.readable_iban, self.bic)

    @property
    def iban_readable(self):
        return ' '.join(self.iban[i:i + 4] for i in range(0, len(self.iban), 4))

    @property
    def mask_iban(self):
        iban = self.readable_cb[0:4] + re.sub(r'[a-zA-Z0-9]', '*', self.iban_readable[4:-4]) + self.iban_readable[-4:]
        return '%s/%s' % (iban, self.bic)

    @property
    def is_valid_ibanlib(self):
        self.iban = re.sub(r'\s+', '', self.iban, flags=re.UNICODE)
        try:
            iban = IBAN(self.iban)
            if not self.bic: self.bic = str(iban.bic)
            return True
        except ValueError:
            return False

    @property
    def is_valid_bic(self):
        try:
            if self.bic:
                BIC(self.bic)
            return True
        except ValueError:
            return False

    @property
    def is_exist_iban(self):
        if ShopConfig.subscription_for == 'group':
            qs = type(self).objects.filter(iban=self.iban, bic=self.bic, group=self.group)
        else:
            qs = type(self).objects.filter(iban=self.iban, bic=self.bic, user=self.user)
        if self.pk: qs = qs.exclude(pk=self.pk)
        return False if qs.exists() else True

    @property
    def is_valid_iban(self):
        if not settings.DEBUG and self.iban in sepas_test():
            raise ValidationError(code='invalid_iban', message='invalid IBAN')
        if not self.iban or not self.is_valid_ibanlib:
            raise ValidationError(code='invalid_iban', message='invalid IBAN')
        if not self.is_valid_bic:
            raise ValidationError(code='invalid_bic', message='invalid BIC')
        if not self.is_exist_iban:
            raise ValidationError(code='already_iban', message='IBAN already exist')
