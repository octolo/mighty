from django.conf import settings
from mighty.applications.messenger.backends import sendinblue_email, sendinblue_sms

class MissiveBackend(sendinblue_email.MissiveBackend, sendinblue_sms.MissiveBackend):
    pass