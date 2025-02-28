from django.urls import include, path

from mighty.applications.chat import consumers

app_name = 'messenger'
urlpatterns = [
    path('messenger/', include([
        path('chat/<str:room_name>/', consumers.ChatConsumerAsync)])
    ),
]
