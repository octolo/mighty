from django.db import models
from django.contrib.auth import get_user_model

from mighty.models.base import Base
from mighty.models.image import Image
from mighty.functions import setting
from mighty.applications.tenant import managers, translates as _, choices
from mighty.applications.tenant.apps import TenantConfig as conf
from mighty.applications.tenant.decorators import TenantAssociation

CHAT_WITH_TENANTUSERS = "can_chat_with_tenant_users"
@TenantAssociation(related_name='group_tenant', on_delete=models.CASCADE)
class Tenant(Base, Image):
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="roles_tenant", blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_tenant", null=True, blank=True)
    company_representative = models.CharField(max_length=255, blank=True, null=True)
    sync = models.CharField(max_length=3, choices=_.SYNC, default=_.MY)

    objects = models.Manager()
    objectsB = managers.TenantManager()

    class Meta(Base.Meta):
        abstract = True
        ordering = conf.ordering
        verbose_name = _.v_tenant
        verbose_name_plural = _.vp_tenant
        unique_together = ('user', 'group',)
        permissions = [(CHAT_WITH_TENANTUSERS, _.perm_chat_tenantusers)]

    def __str__(self):
        return self.representation

    @property
    def representation(self):
        return "%s , %s" % (str(self.user), str(self.group))

    @property
    def status(self):
        return choices.ALTERNATE_MAIN

    @property
    def fullname(self):
        return self.user.fullname

    @property
    def image_url(self):
        return self.user.image_url

    @property
    def str_group(self):
        return str(self.group)

    @property
    def uid_group(self):
        return str(self.group.uid)
