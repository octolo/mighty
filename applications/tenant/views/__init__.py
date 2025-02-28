from django.conf import settings

from mighty.applications.tenant.views.role.classic import (
    RoleCheckData as RoleCheckData,
)
from mighty.applications.tenant.views.role.classic import (
    RoleDetail,
    RoleList,
)
from mighty.applications.tenant.views.tenant.classic import (
    CurrentTenant,
    TenantDetail,
    TenantList,
)

if 'rest_framework' in settings.INSTALLED_APPS:
    from mighty.applications.tenant.views.role.drf import (
        RoleDetail as RoleDetail,
    )
    from mighty.applications.tenant.views.role.drf import (
        RoleList as RoleList,
    )
    from mighty.applications.tenant.views.tenant.drf import (  # noqa
        CurrentTenant,
        Sesame,
        TenantDetail,
        TenantList,
        TenantModelViewSet,
    )
