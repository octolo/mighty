from django.db import models

from mighty.fields import JSONField, RichTextField
from mighty.models.base import Base
from mighty.functions import setting
from mighty.applications.tenant import managers, translates as _, choices as _c
from mighty.applications.tenant.decorators import TenantAssociation

@TenantAssociation(related_name='group_config')
class TenantSetting(Base):
    search_fields = ['name']
    name = models.CharField(choices=_c.CONFIG_NAME, max_length=255, blank=True, null=True)
    config_char = models.CharField(max_length=255, blank=True, null=True)
    config_json = JSONField(blank=True, null=True)
    config_rich = RichTextField(blank=True, null=True)
    config_text = models.TextField(blank=True, null=True)

    objects = models.Manager()

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_setting
        verbose_name_plural = _.vp_setting
        ordering = ["name", "group"]
        unique_together = ('id', 'group', 'name')

    def count(self):
        return self.sql_count if hasattr(self, 'sql_count') else self.number
