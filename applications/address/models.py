from django.db import models
from django.core.exceptions import ValidationError
from mighty.models.base import Base
from mighty.applications.address import translates as _, fields, get_address_backend
from mighty.applications.address.apps import AddressConfig as conf
address_backend = get_address_backend()

CHOICES_WAYS = sorted(list(_.WAYS), key=lambda x: x[1])
class AddressNoBase(models.Model):
    backend_id = models.CharField(_.address, max_length=255, null=True, blank=True)
    address = models.CharField(_.address, max_length=255, null=True, blank=True)
    complement = models.CharField(_.complement, max_length=255, null=True, blank=True)
    locality = models.CharField(_.locality, max_length=255, null=True, blank=True)
    postal_code = models.CharField(_.postal_code, max_length=255, null=True, blank=True)
    state = models.CharField(_.state, max_length=255, null=True, blank=True)
    state_code = models.CharField(_.state_code, max_length=255, null=True, blank=True)
    country = models.CharField(_.country, max_length=255, default=conf.Default.country, blank=True, null=True)
    country_code = models.CharField(_.country_code, max_length=255, default=conf.Default.country_code, blank=True, null=True)
    cedex = models.CharField(_.cedex, max_length=255, null=True, blank=True)
    cedex_code = models.CharField(_.cedex_code, max_length=255, null=True, blank=True)
    special = models.CharField(max_length=255, null=True, blank=True)
    index = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    raw = models.CharField(max_length=255, null=True, blank=True)
    enable_clean_fields = False

    class Meta:
        abstract = True
        verbose_name = _.v_address
        verbose_name_plural = _.vp_address

    def fill_from_raw(self):
        address = address_backend.get_location(self.raw)
        if address:
            self.backend_id = address["id"]
            self.source = address["source"]
            for field in fields:
                setattr(self, field, address[field])

    def fill_raw(self):
        if not self.raw:
            if self.country_code:
                formatting = 'format_%s' % self.country_code.lower()
                self.raw = getattr(self, formatting)() if hasattr(self, formatting) else self.format_universal()
            else:
                self.raw = self.format_universal()

    def erase_to_new(self, *args, **kwargs):
        self.backend_id = kwargs.get('backend_id', None)
        self.source = kwargs.get('source', 'FROMUSER')
        self.raw = None
        for field in fields:
            setattr(self, field, kwargs.get(field, None))

    @property
    def has_state_or_postal_code(self):
        return True if self.postal_code or self.state_code else False
    
    def clean_state_or_postal_code(self):
        if not self.has_state_or_postal_code:
            raise ValidationError(_.validate_postal_state_code)

    @property
    def has_address(self):
        return True if self.address else False

    def clean_address(self):
        if not self.has_address:
            raise ValidationError(code='invalid_address', message='invalid address')

    @property
    def has_locality(self):
        return True if self.locality else False

    def clean_locality(self):
        if not self.has_locality:
            raise ValidationError(code='invalid_locality', message='invalid locality')

    def clean_address_fields(self):
        if self.enable_clean_fields:
            self.clean_address()
            #self.clean_locality()
            self.clean_state_or_postal_code()

    @property
    def address_is_usable(self):
        try:
            self.clean_address()
            self.clean_locality()
            self.clean_state_or_postal_code()
        except ValidationError:
            return False
        return True

    @property
    def address_is_empty(self):
        return sum([1 if getattr(self, field) or field != 'raw' else 0 
            for field in fields])

    def only_raw(self):
        if self.address_is_empty and self.raw:
            self.fill_from_raw()

    def save(self, *args, **kwargs):
        self.fill_raw()
        self.clean_address_fields()
        super().save(*args, **kwargs)

    @property
    def state_or_postal_code(self):
        return self.postal_code if self.postal_code else self.state_code

    @property
    def city(self):
        formatting = 'city_%s' % self.country_code.lower()
        return getattr(self, formatting) if hasattr(self, formatting) else self.city_default

    @property
    def city_fr(self):
        cedex = "CEDEX %s" % self.cedex_code if self.cedex_code else ""
        return " ".join([str(ad) for ad in [self.state_or_postal_code, self.locality, cedex] if ad]).strip()

    @property
    def city_default(self):
        return " ".join([str(ad) for ad in [self.state_or_postal_code, self.locality] if ad]).strip()

    @property
    def representation(self):
        return self.raw

    @property
    def raw_address(self):
        return self.raw

    @property
    def fields_used(self):
        return fields

    def format_universal(self):
        tpl = ""
        if self.address: tpl += "%(address)s"
        if self.postal_code: tpl += ", %(postal_code)s" if len(tpl) else "%(postal_code)s"
        if self.locality: tpl += ", %(locality)s"  if len(tpl) else "%(locality)s"
        if self.state: tpl += ", %(state)s" if len(tpl) else "%(state)s"
        if self.country: tpl += ", %(country)s"  if len(tpl) else "%(country)s"
        return tpl % ({field: getattr(self, field) for field in self.fields_used})

class Address(AddressNoBase, Base):
    search_fields = ['locality', 'postal_code']

    class Meta:
        abstract = True
        verbose_name = _.v_address
        verbose_name_plural = _.vp_address