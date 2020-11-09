from django.urls import path, include
from mighty.functions import setting
from mighty.applications.user import views

urlpatterns = [
    path('user/', include([])),
]

api_urlpatterns = [
    path('user/', include([
        path('me/', views.UserMe.as_view(), name="api-user-mydetail"),
        path('invitation/', include([
            path('<uuid:uid>/', views.InvitationDetail.as_view(), name="api-user-invitation"),
            path('<uuid:uid>/<str:action>/', views.InvitationDetail.as_view(), name="api-user-invitation-action"),
        ]))
    ]))
]
