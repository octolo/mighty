from django.utils.translation import gettext_lazy as _

STATUS_PENDING = 'PENDING'
STATUS_REFUSED = 'REFUSED'
STATUS_ACCEPTED = 'ACCEPTED'
STATUS_READY = 'READY'
STATUS = (
    (STATUS_PENDING, _('pending')),
    (STATUS_REFUSED, _('refused')),
    (STATUS_ACCEPTED, _('accepted')),
    (STATUS_READY, _('ready')),
)

ALTERNATE_MAIN = 'MAIN'
ALTERNATE_DEFAULT = 'ALTERNATE'
ALTERNATE_DEPUTY = 'DEPUTY'
ALTERNATE = (
    (ALTERNATE_DEFAULT, _('alternate')),
    (ALTERNATE_DEPUTY, _('deputy')),
)