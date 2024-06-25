from django.db import models


def TenantAssociation(**kwargs):
    def decorator(obj):
        class NewClass(obj):
            group = models.ForeignKey(conf.ForeignKey.group,
                on_delete=kwargs.get('on_delete', models.CASCADE),
                related_name=kwargs.get('related_name', 'group_set'),
                blank=kwargs.get('blank', False),
                null=kwargs.get('null', False),
            )

            class Meta(obj.Meta):
                abstract = True

        NewClass.__name__ = obj.__name__
        return NewClass
    return decorator
