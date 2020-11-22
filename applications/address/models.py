from django.db import models
from mighty.models.base import Base
from mighty.applications.address import translates as _, fields

CHOICES_WAYS = sorted(list(_.WAYS), key=lambda x: x[1])
class Address(Base):
    search_fields = ['locality', 'postal_code']
    default = models.BooleanField(default=False)
    address = models.CharField(_.address, max_length=255, null=True, blank=True)
    complement = models.CharField(_.complement, max_length=255, null=True, blank=True)
    locality = models.CharField(_.locality, max_length=255, null=True, blank=True)
    postal_code = models.CharField(_.postal_code, max_length=255, null=True, blank=True)
    state = models.CharField(_.state, max_length=255, null=True, blank=True)
    state_code = models.CharField(_.state_code, max_length=255, null=True, blank=True)
    country = models.CharField(_.country, max_length=255, null=True, blank=True)
    country_code = models.CharField(_.country_code, max_length=255, null=True, blank=True)
    cedex = models.CharField(_.cedex, max_length=255, null=True, blank=True)
    cedex_code = models.CharField(_.cedex_code, max_length=255, null=True, blank=True)
    special = models.CharField(max_length=255, null=True, blank=True)
    complement = models.CharField(max_length=255, null=True, blank=True)
    index = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = _.v_address
        verbose_name_plural = _.vp_address

    def __str__(self):
        return "%s%s" % ('*' if self.default else '', " ".join([str(getattr(self, field)) for field in fields if getattr(self, field)]))

    def street(self):
        return  " ".join([str(ad) for ad in [self.street_number, self.way, self.route] if ad]).strip()

    def city(self):
        return " ".join([str(ad) for ad in [self.postal_code, self.locality] if ad]).strip()

    def representation(self):
        return "%s%s" % ('*' if self.default else '', " ".join([str(getattr(self, field)) for field in fields if getattr(self, field)]))