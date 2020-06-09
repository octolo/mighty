import json, logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
logger = logging.getLogger(__name__)


class Consumer:
    def __init__(self, ws):
        self._ws = ws

class ChatConsumer(Consumer):
    def __init__(self, ws):
        self.rooms = {}
        super().__init__(ws)

    def default(self, args):
        #room_name = '%s<->%s' % (self._ws.channel_name, args['to'])
        ##logger.info('channel: %s, room: %s' % (self._ws.channel_name, room_name))
        #async_to_sync(self._ws.channel_layer.group_send)(
        #    room_name,
        #    {
        #        'type': 'send_event',
        #        'message': args['msg']
        #    }
        #)
        return {'message': 'send'}

    #def join_support(self, args):
    #    async_to_sync(self.join_room)('%s<->support' % self._ws.channel_name, self._ws.channel_name)
    #    return {'message': 'connected to support'}
#
    #def join_room(self, room_name, channel_name):
    #    if room_name not in self.rooms:
    #        #logger.info('channel: %s, room: %s' % (channel_name, room_name))
    #        async_to_sync(self._ws.channel_layer.group_add)(room_name, channel_name)
    #        self.rooms[room_name] = channel_name
#
    #def leave_room(self, room_name, channel_name):
    #    async_to_sync(self._ws.channel_layer.group_discard)(room_name, channel_name)
    #    del self.rooms[room_name]
    #    return {'message': 'disconnected to the room'}
#
    #def receive(self, message, room_name):
    #    message = json.loads(text_data)
    #    message['type'] = 'message'
    #    async_to_sync(self.channel_layer.group_send)(room_name, message)
#
    #def disconnect(self, close_code):
    #    for room,channel in self.rooms.items():
    #        async_to_sync(self._ws.channel_layer.group_discard)(room, channel)
#
    #def message(self, event):
    #    return {'message': 'chat message'}

class MightyConsumer(WebsocketConsumer):
    consumers = {'chat': ChatConsumer}

    def __init__(self, scope):
        self.actives = {}
        self.test = ''
        super().__init__(scope)

    def uniqid(self, scope):
        if getattr(scope['user'], 'id'): return 'user', scope['user']
        return 'session', scope['session']

    def save_channel(self, typ, obj):
        self.type, self.user = (typ, obj)
        if typ == 'user' and obj.channel != self.channel_name: obj.channel = self.channel_name
        else: obj['channel'] = self.channel_name
        obj.save()

    def connect(self):
        #typ, user = self.uniqid(self.scope)
        #self.save_channel(typ, user)
        self.accept()

    def disconnect(self, close_code):
        self.actives[cmd] = self.consumers[cmd](self)

    def receive(self, text_data):
        #text_data = json.loads(text_data)
        #cmd = text_data.get('cmd')
        #args = text_data.get('args')
        #logger.info('channel: %s, command: %s' % (self.channel_name, cmd))
        async_to_sync(self.command)('chat', {'test': 'toto'})
        #self.send_event(msg)
        
    def command(self, cmd, args):
        if cmd in self.consumers:
            if cmd not in self.actives:
                self.actives[cmd] = self.consumers[cmd](self)
            cmd = self.actives[cmd]
            logger.info('channel: %s, args: %s' % (self.channel_name, args))
            async_to_sync(cmd.default(args))
        #return {'error': 'command not found'}
    
    def send_event(self, event):
        logger.info('channel: %s, event: %s' % (self.channel_name, event))
        self.send(text_data=json.dumps(event))

class AsyncMightyConsumer(AsyncWebsocketConsumer):
    consumers = {}
    actives = {}

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = 'test'
        await self.chat_message({'type': 'chat_message', 'message': message})

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))