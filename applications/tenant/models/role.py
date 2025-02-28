from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from mighty.applications.tenant import managers
from mighty.applications.tenant import translates as _
from mighty.applications.tenant.decorators import TenantAssociation
from mighty.models.base import Base
from mighty.models.image import Image


@TenantAssociation(related_name='group_role')
class Role(Base, Image):
    search_fields = ['name']
    name = models.CharField(max_length=255)
    number = models.PositiveIntegerField(default=0, editable=False)
    three_first = models.CharField(
        max_length=255, editable=False, blank=True, null=True
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = models.Manager()
    objectsB = managers.RoleManager()

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_role
        verbose_name_plural = _.vp_role
        ordering = ['name', 'group']
        unique_together = ('id', 'group', 'name')

    @property
    def count(self):
        return self.get_has('sql_count', 0)

    def set_number(self):
        self.number = self.roles_tenant.count()

    def set_three_first(self):
        self.three_first = ', '.join(
            t.user.username for t in self.roles_tenant.all()[0:2]
        )

    def set_name(self):
        self.name = self.name.lower()

    def pre_save(self):
        self.set_name()

    def pre_update(self):
        self.set_three_first()
        self.set_number()
