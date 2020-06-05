from django.urls import path
from mighty.applications.chat import consumers

app_name = 'chat'
urlpatterns = [
    path('chat/<str:room_name>/', consumers.ChatConsumer),
]