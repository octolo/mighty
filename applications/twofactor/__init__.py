default_app_config = 'mighty.applications.twofactor.apps.TwofactorConfig'

from django.contrib.auth import _get_backends
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import ValidationError, RegexValidator
from mighty.applications.twofactor.apps import TwofactorConfig

class CantIdentifyError(ValidationError):
    def __init__(self, message="We are unable to identify you. Please verify your information or contact support."):
        self.message = message
        self.code = "CantIdentify"
        super().__init__(self.message)

class SpamException(Exception):
    def __init__(self, date, message="[SPAM PROTECTION] You can't send a new message so early. You must wait %s"):
        self.message = message % date
        self.code = "Spam"
        super().__init__(self.message)

def PhoneValidator(target):
    RegexValidator(
        TwofactorConfig.regex.phone,
        '{} is not a valid phone, it must be either +33 or 06...'.format(target),
    )(target) 

def use_twofactor(target):
    for backend, backend_path in _get_backends(return_tuples=True):
        if hasattr(backend, 'by'):
            return backend.by(target, backend_path)
    raise ImproperlyConfigured(
        'No authentication backends have been defined. Does '
        'AUTHENTICATION_BACKENDS contain anything?'
    )

