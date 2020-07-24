from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.applications.tenant import managers, translates as _
from mighty.applications.tenant.apps import TenantConfig as conf
from mighty.applications.user.apps import UserConfig as conf_user

class Role(Base):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True
        verbose_name = _.v_role
        verbose_name_plural = _.vp_role
        ordering = ["name"]

    def __str__(self):
        return self.name.title()

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

CHAT_WITH_TENANTUSERS = "can_chat_with_tenant_users"
class Tenant(Base):
    tenant = models.ForeignKey(conf.ForeignKey.Tenant, on_delete=models.CASCADE, related_name="tenant_tenant")
    roles = models.ManyToManyField(conf.ForeignKey.Role, related_name="tenant_roles")

    # User Or Invitation
    user_or_invitation = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="tenant_userorinvitation", limit_choices_to=conf_user.user_or_inivitation_lct)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('user_or_invitation', 'object_id')

    objects = models.Manager()
    objectsB = managers.TenantManager()

    def __str__(self):
        return "%s , %s" % (str(self.user), str(self.tenant))

    class Meta:
        abstract = True
        verbose_name = _.v_tenant
        verbose_name_plural = _.vp_tenant
        permissions = [(CHAT_WITH_TENANTUSERS, _.perm_chat_tenantusers)]
