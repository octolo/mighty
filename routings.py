from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from mighty.applications.chat.routings import urlpatterns as urls_chat

urlpatterns = []
urlpatterns += urls_chat

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([path('ws/', URLRouter(urlpatterns))])
    ),
})