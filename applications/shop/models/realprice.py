from django.db import models
from mighty.models.base import Base

class RealPrice:
    price = models.PositiveIntegerField(default=0)
    number = models.PositiveIntegerField(default=1)
    tax = models.PositiveIntegerField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True

    @property
    def real_tax(self):
        return (self.price/100)*(self.tax/100) if self.price > 0 else 0

    @property
    def real_price(self):
        return (self.real_tax*self.number)/100 if self.price > 0 else 0

    def set_default_tax(self):
        if not self.tax:
            self.tax = 2000

    def pre_save(self):
        self.set_default_tax()
