from django.db import models


class RoleManager(models.Manager.from_queryset(models.QuerySet)):
    def get_queryset(self):
        from mighty.applications.tenant.apps import TenantConfig as config
        return super().get_queryset()\
            .select_related('group')\
            .annotate(
                sql_count=models.Count(config.count_related, distinct=True),
            )


Selected_related = ('group', 'user')
Prefetch_related = ('roles',)


class TenantManager(models.Manager.from_queryset(models.QuerySet)):
    def get_queryset(self):
        return super().get_queryset()\
            .select_related(*Selected_related)\
            .prefetch_related(*Prefetch_related)\
            .annotate()
