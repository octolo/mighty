from django.urls import path, include
from mighty.applications.twofactor import views

app_name='twofactor'
urlpatterns = [path('accounts/', include(views.TwofactorViewSet().urls)),]
