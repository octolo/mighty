from django.urls import path, include
from tenant import views

app_name = "tenant"
urlpatterns = [path('', include(views.TenantViewSet().urls)),]