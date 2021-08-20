from django.apps import AppConfig
from django.conf import settings
from mighty.functions import setting
from mighty import over_config

class Config:
    pass

if hasattr(settings, 'SHOP'): over_config(Config, settings.SHOP)
class ShopConfig(AppConfig, Config):
    name = 'mighty.applications.shop'
    group = setting('PAYMENT_GROUP', 'auth.Group')
    method = setting('PAYMENT_METHOD', 'mighty.PaymentMethod')
    subscription_for = setting('SUBSCRIPTION_FOR', 'group')
    invoice_backend = setting('INVOICE_BACKEND', 'mighty.applications.shop.backends.stripe')