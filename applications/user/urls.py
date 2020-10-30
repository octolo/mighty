from django.urls import path, include
from mighty.functions import setting
from mighty.applications.user import views

urlpatterns = [
    path('user/', include([])),
]

api_urlpatterns = [
    path('user/', include([
        path('style/', views.UserStyle.as_view(), name="api-user-style"),
        path('me/', views.UserMe.as_view(), name="api-user-mydetail"),
        path('invitation/<uuid:uid>/<str:action>/', views.InvitationAction.as_view()),
    ]))
]
