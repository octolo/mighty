from django.urls import path, include
from mighty.functions import setting
from mighty.applications.user.views import UserViewSet, UserRegister

urlpatterns = [path('accounts/', include(UserViewSet().urls)),]
if 'rest_framework' in setting('INSTALLED_APPS'):
    from mighty.applications.user.views import UserApiViewSet
    urlpatterns += [path('api/accounts/', include(UserApiViewSet().urls)),]