from django.urls import path, include
from mighty.applications.tenant import views

app_name = 'tenant'
api_urlpatterns = [
    path('tenant/', include([
        path('', views.TenantList.as_view(), name="api-tenant-list"),
        path('<uuid:uid>/', views.TenantDetail.as_view(), name="api-tenant-detail"),
        path('<uuid:uid>/current/', views.CurrentTenant.as_view(), name="api-tenant-current"),
        #path('invitation/', include([
        #    path('', views.InvitationList.as_view(), name="api-invitation-exist"),
        #    path('<uuid:uid>/', views.InvitationDetail.as_view(), name="api-tenant-invitation"),
        #    path('<uuid:uid>/<str:action>/', views.InvitationDetail.as_view(), name="api-tenant-invitation-action"),
        #])),
        path('role/', include([
            path('', views.RoleList.as_view(), name="api-role-list"),
            path('<uuid:uid>/', views.RoleDetail.as_view(), name="api-role-detail"),
            path('exist/',  views.RoleCheckData.as_view(), name="api-role-exist"),
        ])),
        path('setting/', include([
            path('', views.TenantSettingList.as_view(), name="api-tenant-setting-list"),
            path('<uuid:uid>/', views.TenantSettingDetail.as_view(), name="api-tenant-setting-detail"),
            path('exist/',  views.TenantSettingCheckData.as_view(), name="api-tenant-setting-exist"),
        ])),
    ])),
]