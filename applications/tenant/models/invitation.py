from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from mighty.models.base import Base
from mighty.applications.tenant import translates as _
from mighty.applications.tenant.apps import TenantConfig as conf
from mighty.applications.user import choices as user_choices
from mighty.applications.user.apps import UserConfig as user_conf
from mighty.applications.tenant.decorators import TenantAssociation

from datetime import datetime
import uuid

#by_method = (
#    ('USER', 'user'),
#    ('TOKEN', 'token'),
#    ('EMAIL', 'email')
#)
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
        self.status = user_choices.STATUS_EXPIRED
        self.save()

    def accepted(self, user):
        self.status = user_choices.STATUS_ACCEPTED
        self.user = user
        user.user_email.get_or_create(email=self.email)
        self.save()

    def refused(self, user):
        self.status = user_choices.STATUS_REFUSED
        self.user = user
        self.save()
