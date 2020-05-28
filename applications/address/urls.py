from django.urls import path, include
from mighty.applications.address import views

app_name='address'
urlpatterns = [path('address/', include(views.AddressViewSet().urls)),]
