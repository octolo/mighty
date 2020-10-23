from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.applications.tenant import managers, translates as _
from mighty.applications.tenant.apps import TenantConfig as conf

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
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="tenant_group")
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="tenant_roles", blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="tenant_user", null=True, blank=True)
    invitation = models.ForeignKey(conf.ForeignKey.invitation, on_delete=models.CASCADE, related_name="tenant_invitation", null=True, blank=True)

    objects = models.Manager()
    objectsB = managers.TenantManager()

    def __str__(self):
        return "%s , %s" % (str(self.user), str(self.group))

    class Meta:
        abstract = True
        verbose_name = _.v_tenant
        verbose_name_plural = _.vp_tenant
        permissions = [(CHAT_WITH_TENANTUSERS, _.perm_chat_tenantusers)]

    @property
    def representation(self):
        return self.user.representation if self.user else self.invitation.representation
