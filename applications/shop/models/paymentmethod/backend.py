from django.utils.module_loading import import_string
from mighty.applications.shop.apps import ShopConfig

class BackendModel:
    def get_backend(self):
        return import_string(ShopConfig.invoice_backend)(ShopConfig.invoice_backend, payment_method=self)

    def valid_backend(self):
        backend = self.get_backend()
        backend.add_pm()