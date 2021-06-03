from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from mighty.applications.user.apps import UserConfig as user_conf
from mighty.applications.messenger import choices

def MissiveFollower(**kwargs):
    def decorator(obj):

        class MFModel(obj):
            priority = models.PositiveIntegerField(default=0, choices=choices.PRIORITIES)
            missive = models.ForeignKey(user_conf.ForeignKey.missive, 
                on_delete=kwargs.get('on_delete', models.CASCADE),
                related_name=kwargs.get('related_name', 'group_set'),
                blank=kwargs.get('blank', True),
                null=kwargs.get('null', True),
            )
            missives = GenericRelation(user_conf.ForeignKey.missive)
            
            class Meta(obj.Meta):
                abstract = True

        return MFModel
    return decorator