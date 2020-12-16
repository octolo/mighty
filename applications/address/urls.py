from django.conf import settings
from django.urls import path, include
from mighty.applications.address import views

app_name="address"
urlpatterns = []
api_urlpatterns = [
    path('address/', views.LocationDetail.as_view(), name="api-address"),
    path('addresses/', views.LocationList.as_view(), name="api-addresses"),
]