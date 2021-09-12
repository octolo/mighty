from django.urls import path, include
from mighty.functions import setting
from mighty.applications.user import views

urlpatterns = [
    path('user/', include([
        path('create/', views.CreateUserView.as_view(), name="use-create"),
    ])),
]

api_urlpatterns = [
    path('user/', include([
        path('form/', include([
            path('create/', views.CreatUserFormView.as_view(), name="api-user-form-create"),
        ])),
        path('check/', include([
            path('email/', views.UserEmailCheckView.as_view(), name="api-user-check-email"),
            path('phone/', views.UserPhoneCheckView.as_view(), name="api-user-check-phone"),
        ])),
        path('', views.CreateUserView.as_view(), name="api-user-profile"),
        path('profile/', views.ProfileView.as_view(), name="api-user-profile"),
        path('invitation/', include([
            path('<uuid:uid>/', views.InvitationDetailView.as_view(), name="api-user-invitation"),
            path('<uuid:uid>/<str:action>/', views.InvitationDetailView.as_view(), name="api-user-invitation-action"),
        ]))
    ]))
]
