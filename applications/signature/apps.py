from django.apps import AppConfig
from django.conf import settings
from mighty.functions import setting
from mighty import over_config

class Config:
    signature_backend = setting('SIGNATURE_BACKEND', 'mighty.applications.signature.backends.docage.SignatureBackend')

if hasattr(settings, 'SIGNATURE'): over_config(Config, settings.SIGNATURE)
class SignatureConfig(AppConfig, Config):
    name = 'mighty.applications.signature'
