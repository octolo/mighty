from django.conf import settings
from django.urls import path, include
from mighty.applications.address import views

app_name="address"
urlpatterns = []
api_urlpatterns = [
    path('address/', include([
        path('', views.LocationDetail.as_view(), name="api-address"),
        path('list/', views.LocationList.as_view(), name="api-addresses"),
        path('form/', views.AddresFormDescView.as_view(), name="api-form"),
    ]))
]