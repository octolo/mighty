default_app_config = 'mighty.applications.signature.apps.SignatureConfig'

from django.apps import apps as django_apps
from django.utils.module_loading import import_string
from mighty.applications.signature.apps import SignatureConfig as conf

def get_signature_backend(path=None):
    path = path if path else conf.signature_backend
    return import_string(path), path

def get_transaction_model(model=conf.transaction_relation):
    transaction = model.split('.')
    return django_apps.get_model(transaction[0], transaction[1])
