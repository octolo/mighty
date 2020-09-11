default_app_config = 'mighty.applications.twofactor.apps.TwofactorConfig'

from django.contrib.auth import _get_backends

def use_twofactor(mode, user, target):
    for backend, backend_path in _get_backends(return_tuples=True):
        if hasattr(backend, 'by') and backend.by(mode, user, target, backend_path):
            return True
    return False
