from django.utils.translation import gettext_lazy as _

STATUS_INITIALIZED = 'INITIALIZED'
STATUS_NOTSEND = 'NOTSEND'
STATUS_TOSEND = 'TOSEND'
STATUS_PENDING = 'PENDING'
STATUS_TOREMIND = 'TOREMIND'
STATUS_REFUSED = 'REFUSED'
STATUS_ACCEPTED = 'ACCEPTED'
STATUS_READY = 'READY'
STATUS_EXPIRED = 'EXPIRED'
STATUS_FINISHED = 'FINISHED'
STATUS_ERROR = 'ERROR'
CHOICES_STATUS = (
    (STATUS_INITIALIZED, _('initialized')),
    (STATUS_NOTSEND, _('not send')),
    (STATUS_TOSEND, _('to send')),
    (STATUS_PENDING, _('pending')),
    (STATUS_TOREMIND, _('to remind')),
    (STATUS_REFUSED, _('refused')),
    (STATUS_ACCEPTED, _('accepted')),
    (STATUS_READY, _('ready')),
    (STATUS_EXPIRED, _('expired')),
    (STATUS_FINISHED, _('finished')),
    (STATUS_ERROR, _('error')),
)
