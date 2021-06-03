from django.db import models
from mighty.applications.tenant.apps import TenantConfig as conf

def TenantAssociation(**kwargs):
    def decorator(obj):

        class TAModel(obj):
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

            def save(self, *args, **kwargs):
                if not self.group: self.set_group()
                super().save(*args, **kwargs)

        return TAModel
    return decorator