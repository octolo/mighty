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
GENDER_COMPANY = 'C'
GENDER_ENTITY = 'E'
GENDER_UNDIVIDED = 'U'
GENDER = (
    (GENDER_MAN, _('man')),
    (GENDER_WOMAN, _('woman')),
    (GENDER_COMPANY, _('company')),
    (GENDER_ENTITY, _('Entity')),
    (GENDER_UNDIVIDED, _('Undivided')),
)


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
STATUS = (
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
