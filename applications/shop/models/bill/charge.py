from django.utils.module_loading import import_string

from mighty.applications.shop.apps import ShopConfig


class ChargeModel:
    def get_backend(self):
        return import_string(ShopConfig.invoice_backend)(
            ShopConfig.invoice_backend,
            bill=self,
            payment_method=self.method,
            subscription=self.subscription)

    def try_to_charge(self):
        if not self.paid and self.method is not None and self.method.is_valid:
            self.to_charge()

    def to_charge(self):
        self.backend = ShopConfig.invoice_backend
        backend = self.get_backend()
        backend.try_to_charge()

    def check_bill_status(self):
        backend = self.get_backend()
        return backend.check_bill_status()
