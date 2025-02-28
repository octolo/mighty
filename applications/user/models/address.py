from django.db import models

from mighty.applications.address import fields as address_fields
from mighty.applications.address.models import Address
from mighty.applications.user.apps import UserConfig as conf
from mighty.models import Base


class UserAddress(Address):
    enable_model_change_log = True
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_address')
    enable_clean_fields = True

    def __str__(self):
        return '%s - %s' % (str(self.user), self.representation)

    class Meta(Base.Meta):
        abstract = True

    @property
    def masking(self):
        return '**'

    def set_default_data(self):
        data = 'raw'
        udata = getattr(self.user, data)
        if (self.default or not udata) and udata != getattr(self, data):
            for field in address_fields:
                setattr(self.user, field, getattr(self, field))
            self.user.save()
