from django.urls import path, include
from mighty.applications.tenant import views

app_name = 'tenant'
api_urlpatterns = [
    path('tenant/', include([
        path('', views.TenantList.as_view()),
        path('', views.TenantList.as_view()),
        path('invitation/', include([
            path('', views.InvitationList.as_view(), name="api-invitation-exist"),
            path('<uuid:uid>/', views.InvitationDetail.as_view(), name="api-tenant-invitation"),
            path('<uuid:uid>/<str:action>/', views.InvitationDetail.as_view(), name="api-tenant-invitation-action"),
        ])),
        path('role/', include([
            path('', views.RoleList.as_view(), name="api-role-list"),
            path('exist/',  views.RoleCheckData.as_view(), name="api-role-exist"),
        ])),
    ])),
]