from datetime import date

from django.db import models

from mighty.applications.shop import generate_code_type
from mighty.models.base import Base


class Discount(Base):
    code = models.CharField(
        max_length=50, default=generate_code_type, unique=True
    )
    amount = models.PositiveIntegerField(default=0)
    is_percent = models.BooleanField(default=False)
    date_end = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    def __str__(self):
        return f'{self.code}: {self.date_end} (-{self.amount / 100!s} {self.type_discount})'

    @property
    def type_discount(self):
        return '%' if self.is_percent else '€'

    @property
    def is_valid(self):
        return (self.date_end >= date.today()) if self.date_end else True

    def calcul_price(self, base_price):
        return (
            ((base_price / 100) * self.amount) / 100
            if self.is_percent
            else self.amount / 100
        )

    def new_price(self, base_price):
        return base_price - self.calcul_price(base_price)
