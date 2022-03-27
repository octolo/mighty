from django.urls import path, include
from mighty.applications.messenger import views

app_name = 'messenger'
urlpatterns = [
    path('messenger/', include([
        path('email/viewer/<uuid:uid>/', views.EmailViewer.as_view(), name="messenger-email-viewer"),
    ])),
]