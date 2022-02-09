from django.urls import path, include
from mighty.applications.dataprotect import views

urlpatterns = []

api_urlpatterns = [
    path('dataprotect/', include([
        path('list/', views.ServiceDataView.as_view(), name="api-dataprotect-list"),
    ]))
]
