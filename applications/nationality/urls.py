from django.conf import settings
from django.urls import path, include
from mighty.applications.nationality import views

urlpatterns = [
    path('nationality/', include([
        path('full/<str:language>/', views.DictListView.as_view()),
        path('dict/<str:name>/<str:language>/', views.DictDetailView.as_view())
    ])),
]
