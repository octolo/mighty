from django.conf import settings
from mighty.applications.tenant.views.tenant.classic import (
    TenantList, TenantDetail, CurrentTenant
)

if 'rest_framework' in settings.INSTALLED_APPS:
    from mighty.applications.tenant.views.tenant.drf import (
        TenantList, TenantDetail, CurrentTenant, TenantModelViewSet, Sesame
    )


