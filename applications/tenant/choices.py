from django.utils.translation import gettext_lazy as _

STATUS_PENDING = 'PENDING'
STATUS_REFUSED = 'REFUSED'
STATUS_ACCEPTED = 'ACCEPTED'
STATUS = (
    (STATUS_PENDING, _('pending')),
    (STATUS_REFUSED, _('refused')),
    (STATUS_ACCEPTED, _('accepted')),
)
