from django.db import models
from django.conf import settings

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
    tenant = models.ForeignKey(conf.ForeignKey.Tenant, on_delete=models.CASCADE, related_name="tenant_tenant")
    user = models.ForeignKey(conf.ForeignKey.User, on_delete=models.CASCADE, related_name="user_tenant")
    roles = models.ManyToManyField(conf.ForeignKey.Role)

    objects = models.Manager()
    objectsB = managers.TenantManager()

    permissions = [(CHAT_WITH_TENANTUSERS, _.perm_chat_tenantusers)]

    def __str__(self):
        return "%s , %s" % (str(self.user), str(self.tenant))

    class Meta:
        abstract = True
        verbose_name = _.v_tenant
        verbose_name_plural = _.vp_tenant
        #permission = ("chat",)
        ordering = ["user__last_name", "user__first_name", "user__username"]

class Invitation(Base):
    tenant = JSONField(dict({"tenant": None, "user": None, "roles": []}))
    email = models.EmailField()
    html = models.TextField()
    txt = models.TextField()
    state = models.PositiveSmallIntegerField(choices=_.STATE, default=0)
    by = models.ForeignKey(conf.ForeignKey.User, on_delete=models.CASCADE, related_name="by_invitation")

    class Meta:
        abstract = True
        verbose_name = _.v_invitation
        verbose_name_plural = _.vp_invitation
        #permission = ("invitation")
        ordering = ["date_create",]

    def set_tenant(self, tenant):
        self.roles["tenant"] = tenant.id

    def set_user(self, user):
        self.roles["user"] = user.id

    def set_roles(self, roles):
        self.roles["roles"] = [role.id for role in roles]

    def on_accept(self):
        tenant = Tenant()
        user = Tenant.user.objects.get(id=self.tenant["user"])
        tenant = Tenant.tenant.objects.get(id=self.tenant["tenant"])
        tenant, tenant_created = Tenant.objectsB.get_or_create(tenant=tenant, user=user)
        tenant.roles.add(*Role.objects.filter(id__in=self.tenant["roles"]))

    def save(self, *args, **kwargs):
        if self.state == 1: self.on_accept()
        super().save(*args, **kwargs)