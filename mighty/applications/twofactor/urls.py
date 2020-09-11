from django.urls import path, include
from mighty.applications.twofactor import views

app_name='twofactor'
urlpatterns = []
api_urlpatterns = [
    path('twofactor/', include([
        path('sendcode/', views.APISendCode.as_view())
    ])),
]
