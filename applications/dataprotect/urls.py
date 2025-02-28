from django.urls import include, path

from mighty.applications.dataprotect import views

urlpatterns = []

api_urlpatterns = [
    path(
        'dataprotect/',
        include([
            path(
                '', views.ServiceDataView.as_view(), name='api-dataprotect-list'
            ),
            path(
                'list/',
                views.ServiceDataView.as_view(),
                name='api-dataprotect-list',
            ),
        ]),
    )
]
