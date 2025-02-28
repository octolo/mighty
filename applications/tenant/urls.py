from django.urls import include, path

from mighty.applications.tenant import views

app_name = 'tenant'
api_urlpatterns = [
    path('tenant/', include([
        path('', views.TenantList.as_view(), name='api-tenant-list'),
        path('<uuid:uid>/', views.TenantDetail.as_view(), name='api-tenant-detail'),
        path('<uuid:uid>/current/', views.CurrentTenant.as_view(), name='api-tenant-current'),
        path('<uuid:uid>/current/sesame/', views.Sesame.as_view(), name='api-tenant-sesame'),
        path('role/', include([
            path('', views.RoleList.as_view(), name='api-role-list'),
            path('<uuid:uid>/', views.RoleDetail.as_view(), name='api-role-detail'),
            path('exist/', views.RoleCheckData.as_view(), name='api-role-exist'),
        ])),
    ])),
]
