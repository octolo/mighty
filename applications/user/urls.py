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
        path('exist/', include([
            path('email/', views.EmailAlreadyExist.as_view(), name="api-user-emailexist"),
            path('phone/', views.PhoneAlreadyExist.as_view(), name="api-user-phoneexist"),
        ])),
        path('me/', views.UserMe.as_view(), name="api-user-mydetail"),
        path('invitation/', include([
            path('<uuid:uid>/', views.InvitationDetail.as_view(), name="api-user-invitation"),
            path('<uuid:uid>/<str:action>/', views.InvitationDetail.as_view(), name="api-user-invitation-action"),
        ]))
    ]))
]
