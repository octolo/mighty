from django.contrib.auth import _get_backends

def send_sms(user):
    for backend, backend_path in _get_backends(return_tuples=True):
        if hasattr(backend, 'send_sms') and backend.send_sms(user, backend_path):
            return True
    return False

def send_email(user):
    for backend, backend_path in _get_backends(return_tuples=True):
        if hasattr(backend, 'send_email') and backend.send_email(user, backend_path):
            return True
    return False