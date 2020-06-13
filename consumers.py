import json, logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from mighty.apps import MightyConfig as conf
from mighty.models import Channel
logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, ws):
        self._ws = ws

class MightyConsumer(WebsocketConsumer):
    consumers = {}
    delimiter = conf.Channel.delimiter

    def __init__(self, scope):
        self.actives = {}
        self.rooms = {}
        super().__init__(scope)

    @property
    def uid(self, user=None):
        if user: return user.uid if hasattr(self.user, 'uid') else user['hashnonymous']
        return self.user.uid if hasattr(self.user, 'uid') else self.user['hashnonymous']

    def uniqid(self, scope):
        if getattr(scope['user'], 'id'): return 'user', scope['user']
        return 'session', scope['session']

    def save_channel(self, typ, obj):
        self.type, self.user = (typ, obj)
        if typ == 'user' and obj.channel != self.channel_name: obj.channel = self.channel_name
        else: obj['channel'] = self.channel_name
        obj.save()

    def join_room(self, room_name):
        if room_name not in self.rooms:
            async_to_sync(self.channel_layer.group_add)(room_name, self.channel_name)
            self.rooms[room_name] = self.channel_name
            self.send_event({'status': True, 'event': 'chat.connected.%s:chat' % room_name.split(self.delimiter)[1]})

    def leave_room(self, room_name):
        if room_name in self.rooms:
            asyn_to_sync(self.channel_layer.group_discard)(room_name, self.channel_name)
            del self.rooms[room_name]
            self.send_event({'status': True, 'event': 'chat.leave.%s:chat' % room_name.split(self.delimiter)[1]})

    def send_to_room(self, room_name, event, datas={}, uid=True):
        datas['type'] = 'send.event'
        if uid: datas['uid'] = str(self.uid)
        async_to_sync(self.channel_layer.group_send)(room_name, datas)
        self.send_event({'status': True, 'event': 'chat.connected.room:chat'})

    def connect(self):
        typ, user = self.uniqid(self.scope)
        self.save_channel(typ, user)
        self.accept()

    def receive(self, text_data):
        text_data = json.loads(text_data)
        cmd = text_data.get('cmd').split('.')[0]
        args = text_data.get('args')
        if cmd in self.consumers:
            if cmd not in self.actives:
                self.actives[cmd] = self.consumers[cmd](self)
            logger.info('cmd: %s, args: %s' % (text_data.get('cmd'), args), extra={'user': self.user})
            self.actives[cmd].default(text_data.get('cmd'), args)
        else:
            self.send_event({'status': False, 'event': 'command.unknown'})

    def send_event(self, event):
        event['self'] ='uid' in event and str(self.uid) == event['uid']
        logger.info('event: %s' % event, extra={'user': self.user})
        self.send(text_data=json.dumps(event))