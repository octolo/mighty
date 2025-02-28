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
    from mighty.applications.tenant.views.role.drf import RoleList as RoleList
    from mighty.applications.tenant.views.tenant.drf import (
        CurrentTenant as CurrentTenant,
    )
    from mighty.applications.tenant.views.tenant.drf import (
        Sesame as Sesame,
    )
    from mighty.applications.tenant.views.tenant.drf import (
        TenantDetail as TenantDetail,
    )
    from mighty.applications.tenant.views.tenant.drf import (
        TenantList as TenantList,
    )
    from mighty.applications.tenant.views.tenant.drf import (
        TenantModelViewSet as TenantModelViewSet,
    )
