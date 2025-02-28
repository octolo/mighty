from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from mighty.applications.tenant.apps import TenantConfig as conf


def TenantAssociation(**kwargs):
    def decorator(obj):
        class_name = obj.__name__.lower()

        class NewClass(obj):
            tenant_association_config = kwargs
            tenant_field = kwargs.get('tenant_field', 'tenant')

            group_relations = kwargs.get('group_relations', [])
            group = models.ForeignKey(
                conf.ForeignKey.group,
                on_delete=kwargs.get('on_delete', models.CASCADE),
                related_name=kwargs.get('related_name', 'group_set'),
                blank=kwargs.get('blank', False),
                null=kwargs.get('null', False),
            )

            if kwargs.get('user_related'):
                user = models.ForeignKey(
                    get_user_model(),
                    related_name=class_name + '_user_related',
                    on_delete=models.SET_NULL,
                    blank=True,
                    null=True,
                )
            if kwargs.get('roles_related'):
                roles = models.ManyToManyField(
                    conf.ForeignKey.role,
                    related_name=class_name + '_roles_related',
                    blank=True,
                )

            class Meta(obj.Meta):
                abstract = True

            def groups_m2m(self, field):
                return [obj.group.id for obj in getattr(self, field).all()]

            @property
            def is_group_coherence(self):
                if len(self.group_relations):
                    groups = []
                    for rel in self.group_relations:
                        if self.fields().get(rel) == 'ManyToManyField':
                            groups += self.groups_m2m(rel)
                        else:
                            groups.append(getattr(self, rel).id)
                    groups = list(dict.fromkeys(groups))
                    return bool(
                        not len(groups)
                        or (len(groups) == 1 and groups[0] == self.group.id)
                    )
                return True

            def check_group_coherence(self):
                if not self.is_group_coherence:
                    raise ValidationError('groups relation are not coherent')

            # User related (direct relation)
            def get_user_related(self):
                return (
                    getattr(self, self.tenant_field)
                    if hasattr(self, self.tenant_field)
                    else None
                )

            def set_user_related(self):
                if kwargs.get('user_related') and not self.user:
                    self.user = self.get_user_related()

            # Users related (indirect m2m relation)
            def get_users_related(self, ur):
                return self.ur.values_list('id', flat=True)

            def set_users_related(self):
                for ur in kwargs.get('users_related', []):
                    ur_name = str(ur) + '_list_id'
                    if hasattr(self, ur_name):
                        setattr(self, ur_name, self.get_users_related(ur))

            def tenant_association_update(self):
                self.set_user_related()
                self.set_users_related()

            def tenant_pre_save(self):
                if self.group:
                    for field in kwargs.get('duplicate_db_charfields', ()):
                        setattr(
                            self, 'group_' + field, getattr(self.group, field)
                        )

            # def save(self, *args, **kwargs):
            #    if not self.group:
            #        try:
            #            self.set_group()
            #        except AttributeError:
            #            pass
            #    self.check_group_coherence()
            #    super().save(*args, **kwargs)

        for field in kwargs.get('duplicate_db_charfields', ()):
            NewClass.add_to_class(
                'group_' + field,
                models.CharField(max_length=255, blank=True, null=True),
            )

        NewClass.__name__ = obj.__name__
        return NewClass

    return decorator


def TenantGroup(**kwargs):
    def decorator(obj):
        class NewClass(obj):
            nbr_tenant = models.PositiveBigIntegerField(
                default=1, editable=False
            )

            def set_nbr_tenant(self):
                if self.pk:
                    self.nbr_tenant = self.group_tenant.count()

            class Meta(obj.Meta):
                abstract = True

            def save(self, *args, **kwargs):
                self.set_nbr_tenant()
                super().save(*args, **kwargs)

        NewClass.__name__ = obj.__name__
        return NewClass

    return decorator
