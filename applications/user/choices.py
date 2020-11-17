from django.utils.translation import gettext_lazy as _

METHOD_CREATESU = 'CREATESUPERUSER'
METHOD_BACKEND = 'BACKEND'
METHOD_FRONTEND = 'FRONTEND'
METHOD_IMPORT = 'IMPORT'
METHOD = (
    (METHOD_CREATESU, _('Manage.py createsuperuser')),
    (METHOD_BACKEND, _('Backend (/admin)')),
    (METHOD_FRONTEND, _('Workflow allowed by your website')),
    (METHOD_IMPORT, _('By import')),
)

GENDER_MAN = 'M'
GENDER_WOMAN = 'W'
GENDER = (
    (GENDER_MAN, _('man')),
    (GENDER_WOMAN, _('woman')),
)

STATUS_NOTSEND = 'NOTSEND'
STATUS_TOSEND = 'TOSEND'
STATUS_PENDING = 'PENDING'
STATUS_REFUSED = 'REFUSED'
STATUS_ACCEPTED = 'ACCEPTED'
STATUS_EXPIRED = 'EXPIRED'
STATUS = (
    (STATUS_NOTSEND, _('not send')),
    (STATUS_TOSEND, _('to send')),
    (STATUS_PENDING, _('pending')),
    (STATUS_REFUSED, _('refused')),
    (STATUS_ACCEPTED, _('accepted')),
    (STATUS_EXPIRED, _('expired')),
)
