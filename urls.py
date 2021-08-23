from django.conf import settings
from django.urls import path, include
from mighty.apps import MightyConfig as conf
from mighty.views import Widget, Config, ConfigListView, ConfigDetailView, GenericSuccess

app_name = "mighty"
urlpatterns = [
    path('success/', GenericSuccess.as_view(), name="generic-success"),
    path('widgets/<str:widget>/<str:id>/', Widget.as_view(), name="mighty-widget"),
]
api_urlpatterns = [path('config/', include([
        path('base/', Config.as_view(), name="api-config-base"),
        path('full/', ConfigListView.as_view(), name="api-config-full"),
        path('<str:name>/', ConfigDetailView.as_view(), name="api-config-name"),
    ])
)]

# Enable app nationality
if "mighty.applications.nationality" in settings.INSTALLED_APPS:
    from mighty.applications.nationality import urls as urls_nationality
    api_urlpatterns += urls_nationality.urlpatterns

# Enable app user
if "mighty.applications.user" in settings.INSTALLED_APPS:
    from mighty.applications.user import urls as urls_user
    urlpatterns += urls_user.urlpatterns
    if hasattr(urls_user, 'api_urlpatterns'):
        api_urlpatterns += urls_user.api_urlpatterns

# Enable app tenant
if "mighty.applications.tenant" in settings.INSTALLED_APPS:
    from mighty.applications.tenant import urls as urls_tenant
    if hasattr(urls_tenant, 'urlpatterns'):
        urlpatterns += urls_tenant.urlpatterns
    if hasattr(urls_tenant, 'api_urlpatterns'):
        api_urlpatterns += urls_tenant.api_urlpatterns

# Enable app twofactor
if "mighty.applications.twofactor" in settings.INSTALLED_APPS:
    from mighty.applications.twofactor import urls as urls_twofactor
    urlpatterns += urls_twofactor.urlpatterns
    if hasattr(urls_twofactor, 'api_urlpatterns'):
        api_urlpatterns += urls_twofactor.api_urlpatterns

# Enable app address
if "mighty.applications.address" in settings.INSTALLED_APPS:
    from mighty.applications.address import urls as urls_address
    if hasattr(urls_address, 'api_urlpatterns'):
        api_urlpatterns += urls_address.api_urlpatterns


# Enable app shop
if "mighty.applications.shop" in settings.INSTALLED_APPS:
    from mighty.applications.address import urls as urls_shop
    urlpatterns += urls_shop.urlpatterns
    if hasattr(urls_shop, 'api_urlpatterns'):
        api_urlpatterns += urls_shop.api_urlpatterns

# Enable app grapher
if "mighty.applications.grapher" in settings.INSTALLED_APPS:
    from mighty.applications.grapher import urls as urls_grapher
    urlpatterns += urls_grapher.urlpatterns

if conf.jwt_enable:
    from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

    api_urlpatterns.append(
        path('token/', include([
            path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            path('obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('verify/', TokenVerifyView.as_view(), name='token_verify'),
        ]))
    )

#Enable app chat
#if "mighty.applications.chat" in settings.INSTALLED_APPS:
#    from mighty.applications.chat.urls import urlpatterns as urls_chat
#    urlpatterns += urls_chat
