from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.template.loader import render_to_string

from mighty.apps import MightyConfig
from mighty.fields import JSONField
from mighty.models import Missive
from mighty.models.base import Base
from mighty.functions import setting
from mighty.applications.tenant import managers, translates as _, choices, get_tenant_model
from mighty.applications.tenant.apps import TenantConfig as conf
from mighty.applications.user import choices as user_choices
from mighty.applications.user.apps import UserConfig as user_conf

from datetime import datetime
import uuid, logging
logger = logging.getLogger(__name__)

class Role(Base):
    search_fields = ['name']
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_role")
    name = models.CharField(max_length=255, unique=True)

    objects = models.Manager()
    objectsB = managers.RoleManager()

    class Meta:
        abstract = True
        verbose_name = _.v_role
        verbose_name_plural = _.vp_role
        ordering = ["name"]

    def __str__(self):
        return self.name.title()

    def count(self):
        return self.sql_count if hasattr(self, 'sql_count') else self.roles_tenant.all().count()

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

CHAT_WITH_TENANTUSERS = "can_chat_with_tenant_users"
class Tenant(Base):
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_tenant")
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="roles_tenant", blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_tenant", null=True, blank=True)
    company_representative = models.CharField(max_length=255, blank=True, null=True)
    invitation = models.ForeignKey(conf.ForeignKey.invitation, on_delete=models.CASCADE, related_name="invitation_tenant", null=True, blank=True, editable=False)

    objects = models.Manager()
    objectsB = managers.TenantManager()

    class Meta:
        abstract = True
        verbose_name = _.v_tenant
        verbose_name_plural = _.vp_tenant
        unique_together = ('user', 'group')
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

class TenantAlternate(Base):
    tenant = models.ForeignKey(conf.ForeignKey.tenant, on_delete=models.CASCADE, related_name="tenant_alternate")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_tenantalternate")
    status = models.CharField(max_length=10, choices=choices.ALTERNATE, default=choices.ALTERNATE_DEFAULT)
    position = models.PositiveSmallIntegerField(blank=True, null=True)
    invitation = models.ForeignKey(conf.ForeignKey.invitation, on_delete=models.CASCADE, related_name="invitation_tenantalternate", null=True, blank=True, editable=False)

    objects = models.Manager()
    objectsB = managers.TenantAlternateManager()

    class Meta:
        abstract = True
        unique_together = ('user', 'tenant')
        permissions = [(CHAT_WITH_TENANTUSERS, _.perm_chat_tenantusers)]

    def __str__(self):
        return self.representation

    @property
    def representation(self):
        return "%s , %s" % (str(self.user), str(self.group))

    @property
    def group(self):
        return self.tenant.group

    @property
    def company_representative(self):
        return self.tenant.company_representative

    @property
    def fullname(self):
        return self.user.fullname

    @property
    def roles(self):
        return self.tenant.roles

    @property
    def str_group(self):
        return str(self.group)

    @property
    def uid_group(self):
        return str(self.group.uid)

class TenantInvitation(Base):
    group = models.ForeignKey(conf.ForeignKey.group, on_delete=models.CASCADE, related_name="group_tenantinv")
    email = models.EmailField()
    by = models.ForeignKey(user_conf.ForeignKey.user, on_delete=models.SET_NULL, related_name='by_invitation_tenant', blank=True, null=True)
    roles = models.ManyToManyField(conf.ForeignKey.role, related_name="roles_tenantinv", blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__icontains': 'tenant'})
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    tenant = models.ForeignKey(conf.ForeignKey.tenant, on_delete=models.SET_NULL, related_name="tenant_invitation", blank=True, null=True)
    
    status = models.CharField(max_length=8, choices=user_choices.STATUS, default=user_choices.STATUS_NOTSEND)
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    missive = models.ForeignKey(user_conf.ForeignKey.missive, on_delete=models.SET_NULL, related_name='missive_tenantinvitation', blank=True, null=True)
    missives = GenericRelation(user_conf.ForeignKey.missive)

    class Meta:
        abstract = True
        unique_together = ('email', 'group')

    def __str__(self):
        return "%s, %s" % (str(self.email), str(self.group))

    @property
    def is_expired(self):
        delta = datetime.now() - self.date_update
        return user_conf.invitation_days <= delta.days

    def expired(self):
        self.status = choices.STATUS_EXPIRED
        self.save()

    def accepted(self, user=None):
        self.status = choices.STATUS_ACCEPTED
        if user and self.email not in user.get_emails():
            user.user_email.create(email=self.email)
        self.save()

    def refused(self):
        self.status = choices.STATUS_REFUSED
        self.save()
