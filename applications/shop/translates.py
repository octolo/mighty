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