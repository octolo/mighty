import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

class ChatConsumer:
    def default(self, args):
        return {'message': 'resolution suivante'}

    def join_room(self, room_name, channel_name):
        async_to_sync(self.channel_layer.group_add)(room_name, channel_name)

    def leave_room(self, room_name, channel_name):
        async_to_sync(self.channel_layer.group_discard)(room_name, channel_name)

    def receive(self, message, room_name):
        message = json.loads(text_data)
        message['type'] = 'message'
        async_to_sync(self.channel_layer.group_send)(room_name, message)

    def message(self, event):
        del message['type']
        self.send(text_data=json.dumps(message))

class MightyConsumer(WebsocketConsumer):
    consumers = {'chat': ChatConsumer}
    actives = {}

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

    def receive(self, text_data):
        text_data = json.loads(text_data)
        cmd = text_data.get('cmd')
        args = text_data.get('args')
        msg = self.command(cmd, args)
        self.json_send(msg)
        
    def command(self, cmd, args):
        if cmd in self.consumers:
            if cmd not in self.actives:
                self.actives[cmd] = self.consumers[cmd]()
            cmd = self.actives[cmd]
            return getattr(cmd, sub)(args) if 'sub' in args else cmd.default(args)
        return {'error': 'command not found'}

    def status(self, message):
        self.send(text_data=json.dumps(message))

    def json_send(self, message):
        self.send(text_data=json.dumps(message))

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