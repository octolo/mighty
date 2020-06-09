import json, logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, ws):
        self._ws = ws

class MightyConsumer(WebsocketConsumer):
    consumers = {}

    def __init__(self, scope):
        print(self.consumers)
        self.actives = {}
        super().__init__(scope)

    @property
    def uid(self):
        return self.user.uid if hasattr(self.user, 'uid') else self.user['hashnonymous']

    def uniqid(self, scope):
        if getattr(scope['user'], 'id'): return 'user', scope['user']
        return 'session', scope['session']

    def save_channel(self, typ, obj):
        self.type, self.user = (typ, obj)
        if typ == 'user' and obj.channel != self.channel_name: obj.channel = self.channel_name
        else: obj['channel'] = self.channel_name
        obj.save()

    def connect(self):
        typ, user = self.uniqid(self.scope)
        self.save_channel(typ, user)
        self.accept()

    def disconnect(self, close_code):
        for name,consumer in self.actives.items():
            consumer.disconnect(close_code)

    def receive(self, text_data):
        text_data = json.loads(text_data)
        cmd = text_data.get('cmd').split('.')[0]
        args = text_data.get('args')
        if cmd in self.consumers:
            if cmd not in self.actives:
                self.actives[cmd] = self.consumers[cmd](self)
            logger.info('cmd: %s, args: %s' % (text_data.get('cmd'), args), extra={'user': self.user})
            self.actives[cmd].default(text_data.get('cmd'), args)
        self.send_event({'message': 'room_name'})

    def send_event(self, event):
        print(event)
        self.send(text_data=json.dumps(event))