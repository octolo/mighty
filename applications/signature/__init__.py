default_app_config = 'mighty.applications.signature.apps.SignatureConfig'

from django.utils.module_loading import import_string
from mighty.applications.signature.apps import SignatureConfig

def get_signature_backend():
    return import_string(SignatureConfig.signature_backend)()
