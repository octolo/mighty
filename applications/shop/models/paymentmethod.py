from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from mighty.models.base import Base
from mighty.apps import MightyConfig
from mighty.applications.shop import generate_code_type, choices
from mighty.applications.shop.decorators import GroupOrUser

from schwifty import IBAN, BIC
from datetime import datetime
from dateutil.relativedelta import relativedelta

@GroupOrUser(related_name="payment_method", blank=True, null=True)
class PaymentMethod(Base):
    #if ShopConfig.subscription_for == 'group':
    #    group = models.ForeignKey(ShopConfig.group, on_delete=models.SET_NULL, blank=True, null=True, related_name="payment_method")
    #else:
    #    from django.contrib.auth import get_user_model
    #    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, null=True, related_name='payment_method')

    form_method = models.CharField(max_length=17, choices=choices.PAYMETHOD, default="CB")
    date_valid = models.DateField(blank=True, null=True)

    # IBAN
    iban = models.CharField(max_length=27, blank=True, null=True)
    bic = models.CharField(max_length=12, blank=True, null=True)

    # CB
    cb = models.CharField(max_length=16, blank=True, null=True)
    cvc = models.CharField(max_length=4, blank=True, null=True)
    month = models.DateField(blank=True, null=True)
    year = models.DateField(blank=True, null=True)

    # SERVICE
    backend = models.CharField(max_length=255, editable=False)
    service_id = models.CharField(max_length=255, editable=False)
    service_detail = models.TextField(editable=False)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    def __str__(self):
        return "%s - %s" % (self.group_or_user, getattr(self, "str_%s" % self.form_method.lower()))

    @property
    def str_cb(self):
        return "%s (%s-%s %s/%s)" % (self.form_method, self.cb, self.cvc, self.month.month, self.year.year)

    @property
    def str_iban(self):
        return "%s (%s/%s)" % (self.form_method, self.iban, self.bic)

    @property
    def iban_readable(self):
        return " ".join(self.iban[i:i+4] for i in range(0, len(self.iban), 4))

    @property
    def is_valid_iban(self):
        try:
            iban = IBAN(self.iban)
            if not self.bic:
                self.bic = iban.bic
                self.save()
            
        except ValueError:
            raise ValidationError(code='code01IBAN', message='invalid IBAN')

    @property
    def is_valid_bic(self):
        try:
            BIC(self.bic)
        except ValueError:
            raise ValidationError(code='code01BIC', message='invalid BIC')

    #def get_cc_number():
    #    if len(sys.argv) < 2:
    #        usage()
    #        sys.exit(1)
    #    return sys.argv[1]

    def sum_digits(self, digit):
        if digit < 10:
            return digit
        else:
            sum = (digit % 10) + (digit // 10)
            return sum

    def validate_luhn(self, cc_num):
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
        if self.month and self.year:
            date_valid = "%s/%s/%s" % ("01", str(self.month.month), str(self.year.year))
            self.date_valid = datetime.strptime(date_valid, '%d/%m/%Y')+relativedelta(months=1)
            return False if self.date_valid < datetime.now() else True
        return False

    @property
    def is_valid_cvc(self):
        return self.cvc

    @property
    def is_valid_cb(self):
        if not self.is_valid_date:
            raise ValidationError(code='code01CBdate', message='invalid date')
        if not self.validate_luhn(self.cb):
            raise ValidationError(code='code02CBnumber', message='invalid number')
        if not self.is_valid_cvc:
            raise ValidationError(code='code03CBcvc', message='invalid cvc')

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
            #self.is_valid_bic
        else:
            self.is_valid_cb

    def clean(self):
        self.check_validity()

    def save(self, *args, **kwargs):
        #self.check_validity()
        super().save(*args, **kwargs)

            