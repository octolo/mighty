from django.conf import settings
from mighty.applications.tenant.views.tenant.classic import (
    TenantList, TenantDetail, CurrentTenant
)
from mighty.applications.tenant.views.role.classic import (
    RoleList, RoleDetail, RoleCheckData
)
from mighty.applications.tenant.views.setting.classic import (
    TenantSettingList, TenantSettingDetail, TenantSettingCheckData
)

__all__ = ()

if 'rest_framework' in settings.INSTALLED_APPS:
    from mighty.applications.tenant.views.tenant.drf import (
        TenantList, TenantDetail, CurrentTenant, TenantModelViewSet
    )
    from mighty.applications.tenant.views.role.drf import (
        RoleList, RoleDetail
    )
    from mighty.applications.tenant.views.setting.drf import (
        TenantSettingList, TenantSettingDetail
    )

    __all__ += (TenantModelViewSet,)

__all__ = (
    TenantList, TenantDetail, CurrentTenant,
    RoleList, RoleDetail, RoleCheckData,
    TenantSettingList, TenantSettingDetail, TenantSettingCheckData
)
