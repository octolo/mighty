# from channels.routing import ProtocolTypeRouter, URLRouter
from django.utils.module_loading import import_string

from mighty.apps import MightyConfig
from mighty.consumers import MightyConsumer

consumers = {
    key: import_string(ws) for key, ws in MightyConfig.consumers.items()
}
MightyConsumer.consumers.update(consumers)
AuthMiddleware = import_string(MightyConfig.auth_consumer)

# application = ProtocolTypeRouter({
#     'websocket': AuthMiddleware(
#         URLRouter([path('mighty.ws', MightyConsumer)])
#     ),
# })
