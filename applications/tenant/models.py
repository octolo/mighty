from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from mighty.fields import JSONField
from mighty.models import Missive
from mighty.models.base import Base
from mighty.applications.tenant import managers, translates as _, choices, get_tenant_model
from mighty.applications.tenant.apps import TenantConfig as conf
from mighty.applications.user import choices as user_choices
from mighty.applications.user.apps import UserConfig as user_conf

from datetime import datetime

class Role(Base):
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_role")
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
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_tenant")
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="roles_tenant", blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_tenant", null=True, blank=True)
    status = models.CharField(max_length=8, choices=choices.STATUS, default=choices.STATUS_PENDING)
    invitation = models.ForeignKey(settings.TENANT_INVITATION, on_delete=models.CASCADE, related_name="invitation_tenant", null=True, blank=True, editable=False)

    objects = models.Manager()
    objectsB = managers.TenantManager()

    def __str__(self):
        return "%s , %s" % (str(self.user) if self.user else self.invitation, str(self.group))

    class Meta:
        abstract = True
        verbose_name = _.v_tenant
        verbose_name_plural = _.vp_tenant
        unique_together = ('user', 'group')
        permissions = [(CHAT_WITH_TENANTUSERS, _.perm_chat_tenantusers)]

    @property
    def representation(self):
        return self.user.representation if self.user else self.invitation.representation

class TenantInvitation(Base):
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_tenantinv")
    email = models.EmailField()
    by = models.ForeignKey(user_conf.ForeignKey.user, on_delete=models.SET_NULL, related_name='by_invitation_tenant', blank=True, null=True)
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="roles_tenantinv", blank=True)
    tenant = models.ForeignKey(settings.TENANT_MODEL, on_delete=models.SET_NULL, related_name="tenant", null=True, blank=True)
    status = models.CharField(max_length=8, choices=user_choices.STATUS, default=user_choices.STATUS_NOTSEND)
    invitation = models.ForeignKey(user_conf.ForeignKey.missive, on_delete=models.SET_NULL, related_name='invitation_tenant', blank=True, null=True)
    missives = GenericRelation(user_conf.ForeignKey.missive)

    class Meta:
        abstract = True
        unique_together = ('email', 'group')

    @property
    def is_expired(self):
        delta = datetime.now() - self.date_update
        return user_conf.invitation_days <= delta.days

    def accepted(self):
        self.status = choices.STATUS_ACCEPTED
        TenantModel = get_tenant_model(settings.TENANT_MODEL)
        self.tenant, status = TenantModel.objects.get_or_create(
            group=self.group,
            user=get_user_model().objects.get(user_email__email=self.email),
            invitation=self
        )
        self.tenant.save()
        self.save()

    def refused(self):
        self.status = choices.STATUS_REFUSED
        self.save()

    def save(self, *args, **kwargs):
        self.status = user_choices.STATUS_ACCEPTED if self.tenant else self.status
        if self.status == user_choices.STATUS_PENDING:
            if not self.invitation:
                self.invitation = Missive(
                    content_type=self.missives.content_type,
                    object_id=self.id,
                    target=self.email,
                    subject='subject: Tenant',
                    html="html: Tenant",
                    txt="txt: Tenant",
                )
                self.invitation.save()
            elif self.is_expired:
                self.new_token()
                self.invitation.status = user_choices.STATUS_PENDING
                self.invitation.save()
        super().save(*args, **kwargs)