from django.db import models

class RoleManager(models.Manager.from_queryset(models.QuerySet)):
    def get_queryset(self):
        return super().get_queryset()\
            .annotate(sql_count=models.Count('roles_tenant'))

Selected_related = ('group', 'user', 'invitation')
Prefetch_related = ('roles',)
class TenantManager(models.Manager.from_queryset(models.QuerySet)):
    def get_queryset(self):
        return super().get_queryset()\
            .select_related(*Selected_related)\
            .prefetch_related(*Prefetch_related)\
            .annotate()
