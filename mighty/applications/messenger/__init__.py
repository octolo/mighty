default_app_config = 'mighty.applications.messenger.apps.MessengerConfig'

from mighty.functions import get_backends
from mighty.applications.messenger.apps import MessengerConfig as conf

def send_missive(missive):
    for backend, backend_path in get_backends(conf.missive_backends, return_tuples=True, path_extend='.MissiveBackend', missive=missive):
        backend.send()
    return False