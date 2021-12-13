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

owner = _("Propriétaire")
form_method = _("Méthode de paiement")
date_valid = _("Date d'expiration")
exports = _('Exports')
card_number = _('Numéro de carte')
iban = _("IBAN")
bic = _("BIC")
signature = _("Signature")
cvc = _("Cryptogramme")
