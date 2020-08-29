from django.urls import path, include
from mighty.functions import setting
from mighty.applications.user import views

urlpatterns = [
    path('user/', include([
        path('style/', views.UserStyle.as_view(), name="user-style")
    ])),
]

if 'rest_framework' in setting('INSTALLED_APPS'):
    api_urlpatterns = [
        path('user/', include([
            path('me/', views.APIMyDetail.as_view(), name="api-user-mydetail")
        ]))
    ]
