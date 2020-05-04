from django.urls import path, include
from mighty.applications.twofactor import views

urlpatterns = [path('twofactor/', include(views.TwofactorViewSet().urls)),]