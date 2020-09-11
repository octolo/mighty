from django.urls import path, include
from mighty.applications.grapher import views

urlpatterns = [
    path('grapher/', include(views.GraphicViewSet().urls)),
]