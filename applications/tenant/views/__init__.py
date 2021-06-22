from django.conf import settings
from mighty.applications.tenant.views.tenant.classic import (
    TenantList, TenantDetail, CurrentTenant
)
from mighty.applications.tenant.views.role.classic import (
    RoleList, RoleDetail, RoleCheckData
)

__all__ = (
    TenantList, TenantDetail, CurrentTenant,
    RoleList, RoleDetail, RoleCheckData
)

if 'rest_framework' in settings.INSTALLED_APPS:
    from mighty.applications.tenant.views.tenant.drf import (
        TenantList, TenantDetail, CurrentTenant, TenantModelViewSet
    )
    from mighty.applications.tenant.views.role.drf import (
        RoleList, RoleDetail
    )

    __all__ += (TenantModelViewSet,)