from django.db import models
from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop import generate_code_type, choices
from mighty.applications.shop.apps import ShopConfig

from schwifty import IBAN, BIC
from datetime import timedelta


class PaymentMethod(Base):
    group = models.ForeignKey(ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True, related_name="payment_method")
    form_method = models.CharField(max_length=4, choices=choices.PAYMETHOD, default="CB")

    # IBAN
    iban = models.CharField(max_length=27, blank=True, null=True)
    bic = models.CharField(max_length=12, blank=True, null=True)
    cb = models.CharField(max_length=16, blank=True, null=True)
    date_valid = models.DateField(blank=True, null=True)

    # SERVICE
    backend = models.CharField(max_length=255, editable=False)
    service_id = models.CharField(max_length=255, editable=False)
    service_detail = models.TextField(editable=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    @property
    def is_valid_iban(self):
        try:
            IBAN(self.compact_iban)
            return True
        except ValueError:
            return False

    @property
    def is_valid_bic(self):
        try:
            BIC(self.bic)
            return True
        except ValueError:
            return False

    def get_cc_number():
        if len(sys.argv) < 2:
            usage()
            sys.exit(1)
        return sys.argv[1]

    def sum_digits(digit):
        if digit < 10:
            return digit
        else:
            sum = (digit % 10) + (digit // 10)
            return sum

    def validate_luhn(cc_num):
        cc_num = cc_num[::-1]
        cc_num = [int(x) for x in cc_num]
        doubled_second_digit_list = list()
        digits = list(enumerate(cc_num, start=1))
        for index, digit in digits:
            if index % 2 == 0:
                doubled_second_digit_list.append(digit * 2)
            else:
                doubled_second_digit_list.append(digit)
        doubled_second_digit_list = [sum_digits(x) for x in doubled_second_digit_list]
        sum_of_digits = sum(doubled_second_digit_list)
        return sum_of_digits % 10 == 0

    @property
    def is_valid_cb(self):
        if self.date_valid:
            return self.validate_luhn(self.cb)
        return False

    @property
    def is_valid(self):
        if self.form_method == "IBAN":
            return (self.is_valid_iban and self.is_valid_bic)
        return self.is_valid_cb

    @property        
    def cb_month(self):
        return self.date_valid.month

    @property
    def cb_year(self):
        return self.date_valid.year
