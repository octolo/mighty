from django.utils.translation import gettext_lazy as _

FREQUENCIES = (
    ('ONUSE', _('Par utilisation')),
    ('MONTH', _('Mensuel')),
    ('YEAR', _('Annuel')),
    ('CUSTOM', _('Custom')),
)

PAYMETHOD = (
    ("CB", "CB"),
    ("IBAN", "IBAN"),
)