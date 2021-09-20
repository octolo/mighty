from django.utils.translation import gettext_lazy as _

v_stock = _('stock')
vp_stock = _('stocks')

YEAR = 'YEAR'
MONTH = 'MONTH'
ONESHOT = 'ONESHOT'

FREQUENCIES = (
    (YEAR, 'YEAR'),
    (MONTH, 'MONTH'),
    (ONESHOT, 'ONESHOT'),
)

error_iban_empty = _('IBAN empty')
error_bic_empty = _('BIC empty')

exports = _('Exports')

card_number = _('Card number')
