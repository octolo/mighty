from django.db import models
from mighty.models.base import Base
from mighty.applications.address import translates as _, fields
from mighty.applications.address.apps import AddressConfig as conf
from django.core.exceptions import ValidationError

CHOICES_WAYS = sorted(list(_.WAYS), key=lambda x: x[1])
class AddressNoBase(models.Model):
    backend_id = models.CharField(_.address, max_length=255, null=True, blank=True)
    address = models.CharField(_.address, max_length=255, null=True, blank=True)
    complement = models.CharField(_.complement, max_length=255, null=True, blank=True)
    locality = models.CharField(_.locality, max_length=255, null=True, blank=True)
    postal_code = models.CharField(_.postal_code, max_length=255, null=True, blank=True)
    state = models.CharField(_.state, max_length=255, null=True, blank=True)
    state_code = models.CharField(_.state_code, max_length=255, null=True, blank=True)
    country = models.CharField(_.country, max_length=255, default=conf.Default.country)
    country_code = models.CharField(_.country_code, max_length=255, default=conf.Default.country_code)
    cedex = models.CharField(_.cedex, max_length=255, null=True, blank=True)
    cedex_code = models.CharField(_.cedex_code, max_length=255, null=True, blank=True)
    special = models.CharField(max_length=255, null=True, blank=True)
    index = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    raw = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = _.v_address
        verbose_name_plural = _.vp_address

    #@property
    #def check_postal_state_code(self):
    #    if not self.postal_code and not self.state_code:
    #        return False
    #    return True
    #
    #def clean_postal_state_code(self):
    #    if not self.check_postal_state_code:
    #        raise ValidationError(_.validate_postal_state_code)

    @property
    def street(self):
        return  " ".join([str(ad) for ad in [self.street_number, self.way, self.route] if ad]).strip()

    @property
    def city(self):
        return " ".join([str(ad) for ad in [self.postal_code, self.locality] if ad]).strip()

    @property
    def representation(self):
        return " ".join([str(getattr(self, field)) for field in fields if getattr(self, field)])

    @property
    def raw_address(self):
        return self.raw

    @property
    def fields_used(self):
        return fields

class Address(AddressNoBase, Base):
    search_fields = ['locality', 'postal_code']

    class Meta:
        abstract = True
        verbose_name = _.v_address
        verbose_name_plural = _.vp_address

    #def clean(self):
        #self.clean_postal_state_code()
        #super().clean()

    def save(self, *args, **kwargs):
        #self.clean_postal_state_code()
        super().save(*args, **kwargs)