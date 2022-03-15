from django.utils.translation import gettext_lazy as _

STATUS_PENDING = 'PENDING'
STATUS_REFUSED = 'REFUSED'
STATUS_ACCEPTED = 'ACCEPTED'
STATUS = (
    (STATUS_PENDING, _('pending')),
    (STATUS_REFUSED, _('refused')),
    (STATUS_ACCEPTED, _('accepted')),
)

GSTATUS_INACTIVE = "INACTIVE"
GSTATUS_ACTIVE = "ACTIVE"
GSTATUS_BLOCKED = "BLOCKED"
GSTATUS = (
    (GSTATUS_INACTIVE, _('inactive')),
    (GSTATUS_ACTIVE, _('active')),
    (GSTATUS_BLOCKED, _('blocked')),
)

ALTERNATE_MAIN = 'MAIN'
ALTERNATE_DEFAULT = 'ALTERNATE'
ALTERNATE_DEPUTY = 'DEPUTY'
ALTERNATE = (
    (ALTERNATE_DEFAULT, _('alternate')),
    (ALTERNATE_DEPUTY, _('deputy')),
)

DOMAIN = "DOMAIN"
EMAILPREFIX = "EMAILPREFIX"
SITEWEB = "SITEWEB"
DOMAIN_TR = _("Domaine principal de votre société")
EMAILPREFIX_TR = _("Préfixe pour les emails envoyé par la plateforme prefix@domain.com")
SITEWEB_TR = _("https://domain.com")
CONFIG_NAME = (
    (DOMAIN, DOMAIN_TR),
    (EMAILPREFIX, EMAILPREFIX_TR),
    (SITEWEB, SITEWEB_TR),
)