default_app_config = 'mighty.applications.twofactor.apps.TwofactorConfig'

from django.contrib.auth import _get_backends

def use_twofactor(target):
    for backend, backend_path in _get_backends(return_tuples=True):
        if hasattr(backend, 'by'):
            print('by')
            return backend.by(target, backend_path)
    return False
