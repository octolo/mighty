from django.db import models
from django.core.exceptions import ValidationError
from mighty.applications.tenant.apps import TenantConfig as conf

def TenantAssociation(**kwargs):
    def decorator(obj):

        class TAModel(obj):
            group_relations = kwargs.get('group_relations', [])
            group = models.ForeignKey(conf.ForeignKey.group,
                on_delete=kwargs.get('on_delete', models.CASCADE), 
                related_name=kwargs.get('related_name', 'group_set'),
                blank=kwargs.get('blank', False),
                null=kwargs.get('null', False),
            )
            
            class Meta(obj.Meta):
                abstract = True

            def set_group(self):
                pass

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
                    return True if not len(groups) or (len(groups) == 1 and groups[0] == self.group.id) else False
                return True
                    
            def check_group_coherence(self):
                if not self.is_group_coherence:
                    raise ValidationError('groups relation are not coherent')

            def save(self, *args, **kwargs):
                if not self.group: self.set_group()
                self.check_group_coherence()
                super().save(*args, **kwargs)

        return TAModel
    return decorator