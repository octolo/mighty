from django.urls import include, path

from mighty.applications.user import views

urlpatterns = [
    path(
        'user/',
        include([
            path('create/', views.CreateUserView.as_view(), name='use-create'),
        ]),
    ),
]

api_urlpatterns = [
    path(
        'user/',
        include([
            path(
                'form/',
                include([
                    path(
                        'create/',
                        views.CreatUserFormView.as_view(),
                        name='api-user-form-create',
                    ),
                ]),
            ),
            path(
                'check/',
                include([
                    path(
                        'email/',
                        views.UserEmailCheckView.as_view(),
                        name='api-user-check-email',
                    ),
                    path(
                        'phone/',
                        views.UserPhoneCheckView.as_view(),
                        name='api-user-check-phone',
                    ),
                ]),
            ),
            path('', views.CreateUserView.as_view(), name='api-user-profile'),
            path(
                'profile/', views.ProfileView.as_view(), name='api-user-profile'
            ),
            path(
                'notification/',
                include([
                    path(
                        '',
                        views.NotificationListView.as_view(),
                        name='api-user-notification-list',
                    ),
                    path(
                        '<uuid:uid>/',
                        views.NotificationDetailView.as_view(),
                        name='api-user-notification-detail',
                    ),
                ]),
            ),
        ]),
    )
]
