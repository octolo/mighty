from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from mighty.models.base import Base
from mighty.models.image import Image
from mighty.functions import setting
from mighty.applications.tenant import managers, translates as _, choices
from mighty.applications.tenant.apps import TenantConfig as conf
from mighty.applications.user import choices as user_choices
from mighty.applications.user.apps import UserConfig as user_conf
from mighty.applications.tenant.decorators import TenantAssociation

from datetime import datetime
import uuid, logging
logger = logging.getLogger(__name__)

@TenantAssociation(related_name='group_role')
class Role(Base, Image):
    search_fields = ['name']
    name = models.CharField(max_length=255)
    is_immutable = models.BooleanField(default=False)
    number = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    objectsB = managers.RoleManager()

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_role
        verbose_name_plural = _.vp_role
        ordering = ["name", "group"]
        unique_together = ('id', 'group', 'name')

    def __str__(self):
        return "%s (%s)" % (self.name.title(), str(self.group))

    def count(self):
        return self.sql_count if hasattr(self, 'sql_count') else self.roles_tenant.all().count()

    def pre_save(self):
        self.name = self.name.lower()

    def pre_update(self):
        self.number = self.roles_tenant.count()

CHAT_WITH_TENANTUSERS = "can_chat_with_tenant_users"
@TenantAssociation(related_name='group_tenant')
class Tenant(Base):
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_tenant")
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="roles_tenant", blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_tenant", null=True, blank=True)
    company_representative = models.CharField(max_length=255, blank=True, null=True)
    invitation = models.ForeignKey(conf.ForeignKey.invitation, on_delete=models.CASCADE, related_name="invitation_tenant", null=True, blank=True, editable=False)
    sync = models.CharField(max_length=3, choices=_.SYNC, default=_.MY)

    objects = models.Manager()
    objectsB = managers.TenantManager()

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_tenant
        verbose_name_plural = _.vp_tenant
        unique_together = (('user', 'group'),)
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


by_method = (
    ('USER', 'user'),
    ('TOKEN', 'token'),
    ('EMAIL', 'email')
)
@TenantAssociation(related_name='group_tenantinv')
class TenantInvitation(Base):
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_tenantinv")
    email = models.EmailField()
    by = models.ForeignKey(user_conf.ForeignKey.user, on_delete=models.SET_NULL, related_name='by_invitation_tenant', blank=True, null=True)
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="roles_tenantinv", blank=True)
    tenant = models.ForeignKey(conf.ForeignKey.tenant, on_delete=models.SET_NULL, related_name="tenant_invitation", blank=True, null=True)
    status = models.CharField(max_length=8, choices=user_choices.STATUS, default=user_choices.STATUS_NOTSEND)
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    missive = models.ForeignKey(user_conf.ForeignKey.missive, on_delete=models.SET_NULL, related_name='missive_tenantinvitation', blank=True, null=True)
    missives = GenericRelation(user_conf.ForeignKey.missive)
    user = models.ForeignKey(user_conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_tenantinvitation', blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        unique_together = ('email', 'group')

    def __str__(self):
        return "%s, %s" % (str(self.email), str(self.group))

    @property
    def is_expired(self):
        delta = datetime.now() - self.date_update
        return user_conf.invitation_days <= delta.days

    @property
    def tenant_uid(self):
        return self.tenant.uid if self.tenant else None

    def to_send():
        self.status = user_choices.STATUS_TOSEND

    def expired(self):
        self.status = choices.STATUS_EXPIRED
        self.save()

    def accepted(self, user):
        self.status = choices.STATUS_ACCEPTED
        self.user = user
        user.user_email.get_or_create(email=self.email)
        self.save()

    def refused(self, user):
        self.status = choices.STATUS_REFUSED
        self.user = user
        self.save()
