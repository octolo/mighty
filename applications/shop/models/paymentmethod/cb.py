import re

from django.conf import settings
from django.core.exceptions import ValidationError

from mighty.applications.shop.apps import ShopConfig, cards_test


class CBModel:
    @property
    def readable_cb(self):
        return ' '.join([self.cb[i:i + 4] for i in range(0, len(self.cb), 4)])

    @property
    def str_cb(self):
        return '%s %s %s/%s' % (self.readable_cb, self.cvc, self.date_valid.month, self.date_valid.year)

    @property
    def mask_cb(self):
        cb = self.readable_cb[0:4] + re.sub(r'\d', '*', self.readable_cb[4:-4]) + self.readable_cb[-4:]
        return '%s %s %s/%s' % (cb, self.cvc, self.date_valid.month, str(self.date_valid.year)[-2:])

    def sum_digits(self, digit):
        if digit < 10:
            return digit
        sum = (digit % 10) + (digit // 10)
        return sum

    def validate_luhn(self, cc_num):
        if settings.DEBUG and cc_num in cards_test():
            return True
        cc_num = cc_num[::-1]
        cc_num = [int(x) for x in cc_num]
        doubled_second_digit_list = list()
        digits = list(enumerate(cc_num, start=1))
        for index, digit in digits:
            if index % 2 == 0:
                doubled_second_digit_list.append(digit * 2)
            else:
                doubled_second_digit_list.append(digit)
        doubled_second_digit_list = [self.sum_digits(x) for x in doubled_second_digit_list]
        sum_of_digits = sum(doubled_second_digit_list)
        return sum_of_digits % 10 == 0

    @property
    def is_valid_cvc(self):
        return self.cvc

    @property
    def is_exist_cb(self):
        if ShopConfig.subscription_for == 'group':
            qs = type(self).objects.filter(cvc=self.cvc, cb=self.cb, date_valid=self.date_valid, group=self.group)
        else:
            qs = type(self).objects.filter(cvc=self.cvc, cb=self.cb, date_valid=self.date_valid, user=self.user)
        if self.pk: qs = qs.exclude(pk=self.pk)
        return False if qs.exists() else True

    @property
    def is_valid_cb(self):
        if not self.cb:
            raise ValidationError(code='invalid_cb', message='invalid CB')
        self.cb = re.sub(r'\s+', '', self.cb, flags=re.UNICODE)
        if not self.is_valid_date:
            raise ValidationError(code='invalid_date', message='invalid date')
        if not self.cb or not self.validate_luhn(self.cb):
            raise ValidationError(code='invalid_number', message='invalid number')
        if not self.is_valid_cvc:
            raise ValidationError(code='invalid_cvc', message='invalid cvc')
        if not self.is_exist_cb:
            raise ValidationError(code='already_cb', message='CB already exist')
