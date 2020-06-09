from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from mighty.consumers import MightyConsumer
from mighty.applications.chat.consumers import ChatConsumer

consumers = {'chat': ChatConsumer}
MightyConsumer.consumers = consumers

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([path('mighty.ws', MightyConsumer)])
    ),
})