from django.conf import settings
from django.urls import path, include
from mighty.applications.nationality import views

urlpatterns = [
    path('nationality/', include([
        path('full/', views.DictListView.as_view()),
        path('dict/<str:name>/', views.DictDetailView.as_view())
    ])),
]

api_urlpatterns = [
    path('nationality/', include([
        path('trload/', views.TrLoad.as_view()),
    ])),
]