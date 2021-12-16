from django.utils.translation import gettext_lazy as _

ONEUSE = 'ONEUSE'
MONTH = 'MONTH'
YEAR = 'YEAR'
FREE = 'FREE'
CUSTOM = 'CUSTOM'
FREQUENCIES = (
    (ONEUSE, _('Par utilisation')),
    (MONTH, _('Mensuel')),
    (YEAR, _('Annuel')),
    (FREE, _('Gratuite')),
    (CUSTOM, _('Custom')),
)

CB = "CB"
IBAN = "IBAN"
ACSS_DEBIT = "ACSS_DEBIT"
AFTERPAY_CLEARPAY = "AFTERPAY_CLEARPAY"
ALIPAY = "ALIPAY"
AU_BECS_DEBIT = "AU_BECS_DEBIT"
BACS_DEBIT = "BACS_DEBIT"
BANCONTACT = "BANCONTACT"
BOLETO = "BOLETO"
EPS = "EPS"
FPX = "FPX"
GIROPAY = "GIROPAY"
GRABPAY = "GRABPAY"
IDEAL = "IDEAL"
OXXO = "OXXO"
P24 = "P24"
SOFORT = "SOFORT"
WECHAT_PAY = "WECHAT_PAY"
PAYMETHOD = (
    (CB, "CB"),
    (IBAN, "IBAN"),
    (ACSS_DEBIT, "ACSS_DEBIT"),
    (AFTERPAY_CLEARPAY, "AFTERPAY_CLEARPAY"),
    (ALIPAY, "ALIPAY"),
    (AU_BECS_DEBIT, "AU_BECS_DEBIT"),
    (BACS_DEBIT, "BACS_DEBIT"),
    (BANCONTACT, "BANCONTACT"),
    (BOLETO, "BOLETO"),
    (EPS, "EPS"),
    (FPX, "FPX"),
    (GIROPAY, "GIROPAY"),
    (GRABPAY, "GRABPAY"),
    (IDEAL, "IDEAL"),
    (OXXO, "OXXO"),
    (P24, "P24"),
    (SOFORT, "SOFORT"),
    (WECHAT_PAY, "WECHAT_PAY"),
)

NOTHING = "NOTHING"
NEED_ACTON_URL = "URL"
CHARGE = "CHARGE"
PAID = "PAID"
CHECK = "CHECK"
BILL_STATUS = (
    (NOTHING, _("Nothing")),
    (NEED_ACTON_URL, _("url")),
    (CHARGE, _("To charge")),
    (PAID, _("Paid")),
    (CHECK, _("Check")),
)

PREPARATION = "PREPARATION"
ERROR = "ERROR"
NEED_ACTION = "NEED_ACTION"
VALID = "VALID"
READY = "READY"
DISABLE = "DISABLE"
EXPIRED = "EXPIRED"
SUB_STATUS = (
    (PREPARATION, _("Preparation")),
    (ERROR, _("Error")),
    (NEED_ACTION, _("Need action")),
    (VALID, _("Valid")),
    (READY, _("Ready")),
    (DISABLE, _("Disable")),
    (EXPIRED, _("Expired")),
)