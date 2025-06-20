from django.conf import settings
from django.db import models


class RoleManager(models.Manager.from_queryset(models.QuerySet)):
    def get_queryset(self):
        from mighty.applications.tenant.apps import TenantConfig as config

        return (
            super()
            .get_queryset()
            .select_related('group')
            .annotate(
                sql_count=models.Count(config.count_related, distinct=True),
            )
        )


sr_conf = getattr(settings, 'TENANT_SELECTED_RELATED', ())
Selected_related = ('group', 'user', *sr_conf)

pr_conf = getattr(settings, 'TENANT_PREFETCH_RELATED', ())
Prefetch_related = ('roles', *pr_conf)

class TenantManager(models.Manager.from_queryset(models.QuerySet)):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(*Selected_related)
            .prefetch_related(*Prefetch_related)
            .annotate()
        )
