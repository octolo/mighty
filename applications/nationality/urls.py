from django.conf import settings
from django.urls import path, include
from mighty.applications.nationality import views

urlpatterns = [path('nationality/', include(views.NationalityViewSet().urls)),]
urlpatterns += [path('api/nationality/', include(views.NationalityApiViewSet().urls)),]