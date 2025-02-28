from django.db import models

from mighty.applications.user.apps import UserConfig as conf
from mighty.models import Base


class MergeableAccount(Base):
    primary_user = models.ForeignKey(
        conf.ForeignKey.user,
        on_delete=models.CASCADE,
        related_name='primary_user',
    )
    secondary_user = models.ForeignKey(
        conf.ForeignKey.user,
        on_delete=models.CASCADE,
        related_name='mergeable_user',
    )
    reason = models.CharField(max_length=255)
    is_merged = models.BooleanField(default=False)

    class Meta(Base.Meta):
        abstract = True

    def __str__(self):
        return f'{self.primary_user} - {self.secondary_user}'
