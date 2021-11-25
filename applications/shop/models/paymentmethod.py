from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop import generate_code_type, choices, translates as _
from mighty.applications.shop.decorators import GroupOrUser
from mighty.applications.shop.apps import cards_test, sepas_test

from schwifty import IBAN, BIC
from dateutil.relativedelta import relativedelta
import datetime, re

@GroupOrUser(related_name="payment_method", on_delete=models.SET_NULL, null=True, blank=True)
class PaymentMethod(Base):
    owner = models.CharField(_.owner, max_length=255, blank=True, null=True, help_text="Owner")
    form_method = models.CharField(_.form_method, max_length=17, choices=choices.PAYMETHOD, default="CB")
    date_valid = models.DateField(_.date_valid, blank=True, null=True, help_text="Expire date")
    signature = models.TextField(_.signature, blank=True, null=True)

    # IBAN
    iban = models.CharField(_.iban, max_length=34, blank=True, null=True, help_text="IBAN")
    bic = models.CharField(_.bic, max_length=12, blank=True, null=True, help_text="BIC")

    # CB
    cb = models.CharField(_.card_number, max_length=16, blank=True, null=True, help_text=_.card_number)
    cvc = models.CharField(max_length=4, blank=True, null=True, help_text="CVC")
    month = models.DateField(blank=True, null=True)
    year = models.DateField(blank=True, null=True)

    # SERVICE
    backend = models.CharField(max_length=255, editable=False)
    service_id = models.CharField(max_length=255, editable=False)
    service_detail = models.TextField(editable=False)
    default = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    def __str__(self):
        return "%s - %s" % (self.group_or_user, getattr(self, "str_%s" % self.form_method.lower()))

    @property
    def readable_cb(self):
        return ' '.join([self.cb[i:i+4] for i in range(0, len(self.cb), 4)])

    @property
    def str_cb(self):
        return "%s %s %s/%s" % (self.readable_cb, self.cvc, self.date_valid.month, self.date_valid.year)

    @property
    def mask_cb(self):
        cb = self.readable_cb[0:4]+re.sub(r"\d", '*', self.readable_cb[4:-4])+self.readable_cb[-4:]
        return "%s %s %s/%s" % (cb, self.cvc, self.date_valid.month, str(self.date_valid.year)[-2:])

    @property
    def readable_iban(self):
        return ' '.join([self.iban[i:i+4] for i in range(0, len(self.iban), 4)])

    @property
    def str_iban(self):
        return "%s/%s" % (self.readable_iban, self.bic)

    @property
    def iban_readable(self):
        return " ".join(self.iban[i:i+4] for i in range(0, len(self.iban), 4))

    @property
    def mask_iban(self):
        iban = self.readable_cb[0:4]+re.sub(r"[a-zA-Z0-9]", '*', self.iban_readable[4:-4])+self.iban_readable[-4:]
        return "%s/%s" % (iban, self.bic)

    @property
    def masked(self):
        return getattr(self, "mask_%s" % self.form_method.lower())

    @property
    def is_valid_ibanlib(self):
        self.iban = re.sub(r"\s+", "", self.iban, flags=re.UNICODE)
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
        qs = type(self).objects.filter(iban=self.iban, bic=self.bic)
        if self.pk: qs = qs.exclude(pk=self.pk)
        return False if qs.exists() else True

    @property
    def is_valid_iban(self):
        if not self.iban or not self.is_valid_ibanlib:
            raise ValidationError(code='invalid_iban', message='invalid IBAN')
        if not self.is_valid_bic:
            raise ValidationError(code='invalid_bic', message='invalid BIC')
        if not self.is_exist_iban:
            raise ValidationError(code='already_iban', message='IBAN already exist')

    def sum_digits(self, digit):
        if digit < 10:
            return digit
        else:
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
    def is_valid_date(self):
        if not self.date_valid: 
            print('okkkk')
            return False
        date_valid = datetime.datetime.strptime(self.date_valid, "%Y-%m-%d").date()
        return False if date_valid < datetime.date.today() else True

    @property
    def is_valid_cvc(self):
        return self.cvc

    @property
    def is_exist_cb(self):
        qs = type(self).objects.filter(cvc=self.cvc, cb=self.cb, date_valid=self.date_valid)
        if self.pk: qs = qs.exclude(pk=self.pk)
        return False if qs.exists() else True

    @property
    def is_valid_cb(self):
        self.cb = re.sub(r"\s+", "", self.cb, flags=re.UNICODE)
        if not self.is_valid_date:
            raise ValidationError(code='invalid_date', message='invalid date')
        if not self.cb or not self.validate_luhn(self.cb):
            raise ValidationError(code='invalid_number', message='invalid number')
        if not self.is_valid_cvc:
            raise ValidationError(code='invalid_cvc', message='invalid cvc')
        if not self.is_exist_cb:
            raise ValidationError(code='already_cb', message='CB already exist')

    @property
    def is_valid(self):
        try:
            self.check_validity()
        except ValidationError:
            return False
        return True

    def check_validity(self):
        if self.form_method == "IBAN":
            self.is_valid_iban
        else:
            self.is_valid_cb

    def qs_default(self):
        qs = type(self).objects
        return qs.filter(group=self.group) if hasattr(self, 'group') else qs.filter(user=self.user)

    def has_default(self):
        return self.qs_default().exists()

    def pre_set_default(self):
        if not self.default and not self.has_default():
            self.default = True

    def set_has_default(self):
        self.qs_default.update(default=False)
        self.default = True
        self.save()

    def clean(self):
        self.check_validity()

    def pre_save(self):
        self.check_validity()
        self.pre_set_default()
            