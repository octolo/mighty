from django.db import models

from mighty.models.base import Base


class RealPrice(Base):
    price = models.PositiveIntegerField(default=0)
    number = models.PositiveIntegerField(default=1)
    tax = models.PositiveIntegerField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True

    @property
    def real_tax(self):
        return self.tax / 100 if self.tax else 0

    @property
    def calc_tax(self):
        return (
            round(self.price_ht * (self.real_tax / 100), 2)
            if all([self.price_ht, self.real_tax])
            else 0
        )

    @property
    def price_ht(self):
        return self.price / 100 if self.price else 0

    @property
    def price_ttc(self):
        return (
            self.price_ht + self.calc_tax
            if all([self.price_ht, self.calc_tax])
            else 0
        )

    @property
    def real_price(self):
        return self.price_ttc

    def set_default_tax(self):
        if not self.tax:
            self.tax = 2000

    def pre_save(self):
        super().pre_save()
        self.set_default_tax()
