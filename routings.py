
from django.urls import path
# from channels.routing import ProtocolTypeRouter, URLRouter
from mighty.apps import MightyConfig
from mighty.consumers import MightyConsumer
from mighty.applications.messenger.consumers import ChatConsumer
from django.utils.module_loading import import_string

consumers = {key: import_string(ws) for key, ws in MightyConfig.consumers.items()}
MightyConsumer.consumers.update(consumers)
AuthMiddleware = import_string(MightyConfig.auth_consumer)

# application = ProtocolTypeRouter({
#     'websocket': AuthMiddleware(
#         URLRouter([path('mighty.ws', MightyConsumer)])
#     ),
# })
