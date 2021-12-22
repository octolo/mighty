from django.db import models

from mighty.models.base import Base
from mighty.applications.shop import generate_code_type

from datetime import date

class Discount(Base):
    code = models.CharField(max_length=50, default=generate_code_type, unique=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    is_percent = models.BooleanField(default=False)
    date_end = models.DateField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        ordering = ['date_create']

    def __str__(self):
        return "%s: %s (-%s %s)" % (self.code, self.date_end, self.amount, self.type_discount)

    @property
    def type_discount(self):
        return "%" if self.is_percent else "€"

    @property
    def is_valid(self):
        if self.date_end:
            return (self.date_end >= date.today())
        return True


