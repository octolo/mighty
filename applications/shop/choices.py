from django.utils.translation import gettext_lazy as _

FREQUENCIES = (
    ('ONEUSE', _('Par utilisation')),
    ('MONTH', _('Mensuel')),
    ('YEAR', _('Annuel')),
    ('FREE', _('Gratuite')),
    ('CUSTOM', _('Custom')),
)

PAYMETHOD = (
    ("CB", "CB"),
    ("IBAN", "IBAN"),
    ("ACSS_DEBIT", "ACSS_DEBIT"),
    ("AFTERPAY_CLEARPAY", "AFTERPAY_CLEARPAY"),
    ("ALIPAY", "ALIPAY"),
    ("AU_BECS_DEBIT", "AU_BECS_DEBIT"),
    ("BACS_DEBIT", "BACS_DEBIT"),
    ("BANCONTACT", "BANCONTACT"),
    ("BOLETO", "BOLETO"),
    ("EPS", "EPS"),
    ("FPX", "FPX"),
    ("GIROPAY", "GIROPAY"),
    ("GRABPAY", "GRABPAY"),
    ("IDEAL", "IDEAL"),
    ("OXXO", "OXXO"),
    ("P24", "P24"),
    ("SOFORT", "SOFORT"),
    ("WECHAT_PAY", "WECHAT_PAY"),
)

NEED_ACTON_URL = "URL"

NEED_ACTION = (
    (NEED_ACTON_URL, _("url")),
)