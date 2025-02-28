from django.conf import settings
from django.urls import include, path

from mighty.views import (
    CheckSynchro,
    Config,
    ConfigDetailView,
    ConfigListView,
    GenericSuccess,
    SearchFormDesc,
    Widget,
)

app_name = 'mighty'

urlpatterns = [
    path('success/', GenericSuccess.as_view(), name='generic-success'),
    path('widgets/<str:widget>/<str:id>/', Widget.as_view(), name='mighty-widget'),
]

api_urlpatterns = [
    path('config/', include([
        path('', Config.as_view(), name='api-config-full'),
        path('synchro/', CheckSynchro.as_view(), name='api-config-synchro'),
        path('base/', Config.as_view(), name='api-config-base'),
        path('full/', ConfigListView.as_view(), name='api-config-full'),
        path('<str:name>/', ConfigDetailView.as_view(), name='api-config-name'),
    ])),
    path('form/', include([
        path('search/', SearchFormDesc.as_view(), name='api-form-search'),
    ]))
]
wbh_urlpatterns = []

# Enable app nationality
if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    from mighty.applications.nationality import urls as urls_nationality
    api_urlpatterns += urls_nationality.urlpatterns
    if hasattr(urls_nationality, 'api_urlpatterns'):
        api_urlpatterns += urls_nationality.api_urlpatterns

# Enable app user
if 'mighty.applications.user' in settings.INSTALLED_APPS:
    from mighty.applications.user import urls as urls_user
    urlpatterns += urls_user.urlpatterns
    if hasattr(urls_user, 'api_urlpatterns'):
        api_urlpatterns += urls_user.api_urlpatterns

if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
    from mighty.applications.messenger import urls as urls_messenger
    urlpatterns += urls_messenger.urlpatterns
    if hasattr(urls_messenger, 'api_urlpatterns'):
        api_urlpatterns += urls_messenger.api_urlpatterns
    if hasattr(urls_messenger, 'wbh_urlpatterns'):
        wbh_urlpatterns += urls_messenger.wbh_urlpatterns

# Enable app tenant
if 'mighty.applications.tenant' in settings.INSTALLED_APPS:
    from mighty.applications.tenant import urls as urls_tenant
    if hasattr(urls_tenant, 'urlpatterns'):
        urlpatterns += urls_tenant.urlpatterns
    if hasattr(urls_tenant, 'api_urlpatterns'):
        api_urlpatterns += urls_tenant.api_urlpatterns

# Enable app dataprotect
if 'mighty.applications.dataprotect' in settings.INSTALLED_APPS:
    from mighty.applications.dataprotect import urls as urls_dataprotect
    urlpatterns += urls_dataprotect.urlpatterns
    if hasattr(urls_dataprotect, 'api_urlpatterns'):
        api_urlpatterns += urls_dataprotect.api_urlpatterns

# Enable app address
if 'mighty.applications.address' in settings.INSTALLED_APPS:
    from mighty.applications.address import urls as urls_address
    if hasattr(urls_address, 'api_urlpatterns'):
        api_urlpatterns += urls_address.api_urlpatterns

# Enable app shop
if 'mighty.applications.shop' in settings.INSTALLED_APPS:
    from mighty.applications.shop import urls as urls_shop
    urlpatterns += urls_shop.urlpatterns
    if hasattr(urls_shop, 'api_urlpatterns'):
        api_urlpatterns += urls_shop.api_urlpatterns
    if hasattr(urls_shop, 'webhooks_urlpatterns'):
        webhooks_urlpatterns += urls_shop.webhooks_urlpatterns

# Enable app grapher
if 'mighty.applications.grapher' in settings.INSTALLED_APPS:
    from mighty.applications.grapher import urls as urls_grapher
    urlpatterns += urls_grapher.urlpatterns


# Enable app chat
# if "mighty.applications.chat" in settings.INSTALLED_APPS:
#    from mighty.applications.chat.urls import urlpatterns as urls_chat
#    urlpatterns += urls_chat
