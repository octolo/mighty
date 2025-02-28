from django.urls import include, path

from mighty.applications.nationality import views

urlpatterns = [
    path('nationality/', include([
    ])),
]

api_urlpatterns = [
    path('nationality/', include([
        path('', views.DictListView.as_view()),
        path('full/', views.DictListView.as_view()),
        path('dict/<str:name>/', views.DictDetailView.as_view()),
        path('trload/', views.TrLoad.as_view()),
    ])),
]
