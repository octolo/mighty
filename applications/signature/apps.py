from django.apps import AppConfig
from django.conf import settings
from mighty.functions import setting
from mighty import over_config

class Config:
    # a supprimer
    signature_backend = "mighty.applications.signature.backends.docage.SignatureBackend"
    transaction_relation = setting("SIGNATURE_TRANSACTION_MODEL")
    backend = "mighty.applications.signature.backends.docage"
    signatory_relation = setting("AUTH_USER_MODEL")
    document_relation = setting("SIGNATURE_DOCUMENT_MODEL")

if hasattr(settings, 'SIGNATURE'): over_config(Config, settings.SIGNATURE)
class SignatureConfig(AppConfig, Config):
    name = 'mighty.applications.signature'
