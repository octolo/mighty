default_app_config = 'mighty.applications.twofactor.apps.TwofactorConfig'

from django.contrib.auth import _get_backends
from django.utils import timezone

def use_twofactor(target):
    for backend, backend_path in _get_backends(return_tuples=True):
        if hasattr(backend, 'by'):
            return backend.by(target, backend_path)
    return False

class SpamException(Exception):
    def __init__(self, date, message="[SPAM PROTECTION] You can't send a new message so early. You must wait %s"):
        self.message = message % date
        super().__init__(self.message)