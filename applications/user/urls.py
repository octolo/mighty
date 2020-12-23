from django.urls import path, include
from mighty.functions import setting
from mighty.applications.user import views

urlpatterns = [
    path('user/', include([
        path('create/', views.CreateUser.as_view(), name="use-create"),
    ])),
]

api_urlpatterns = [
    path('user/', include([
        path('check/', include([
            path('email/', views.UserEmailCheck.as_view(), name="api-user-check-email"),
            path('phone/', views.UserPhoneCheck.as_view(), name="api-user-check-phone"),
        ])),
        path('', views.CreateUser.as_view(), name="api-user-profile"),
        path('profile/', views.Profile.as_view(), name="api-user-profile"),
        path('invitation/', include([
            path('<uuid:uid>/', views.InvitationDetail.as_view(), name="api-user-invitation"),
            path('<uuid:uid>/<str:action>/', views.InvitationDetail.as_view(), name="api-user-invitation-action"),
        ]))
    ]))
]
