from django.db import models
#from tenant import queries as q

Selected_related = ('user', 'tenant')
Prefetch_related = ('roles',)
class TenantManager(models.Manager.from_queryset(models.QuerySet)):
    def get_queryset(self):
        return super().get_queryset()\
            .select_related(*Selected_related)\
            .prefetch_related(*Prefetch_related)\
            .annotate()