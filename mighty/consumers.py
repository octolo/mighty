from django.contrib.contenttypes.models import ContentType
import json, logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from mighty.apps import MightyConfig as conf
from mighty.models import Channel
logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, ws):
        self._ws = ws

    def connect(self):
        pass

    def disconnect(self, close_code):
        pass

    def dispatch(self, cmd, args):
        self._ws.send_event({'status': False, 'event': ".".join(cmd)})

class DefaultConsumer(Consumer):
    def dispatch(self, cmd, args):
        if cmd[0] == 'ping':
            self._ws.send_event({'status': True, 'event': 'default.ping'})
        super().dispatch(cmd, args)

class SupervisionConsumer(Consumer):
    def dispatch(self, cmd, args):
        if cmd[1] == 'join':
            self._ws.join_channel('access_support', args['channel'])
        elif cmd[1] == 'leave':
            self._ws.leave_channel('access_support', args['channel'])

class MightyConsumer(WebsocketConsumer):
    consumers = {'default': DefaultConsumer, 'supervision': SupervisionConsumer}
    delimiter = conf.Channel.delimiter

    def __init__(self, scope):
        self.actives = {}
        self.channels_list = {}
        super().__init__(scope)

    def connect(self):
        self.user = self.get_user_obj(self.scope)
        database_sync_to_async(self.save_user_channel)()
        self.accept()

    def disconnect(self, close_code):
        logger.info('disconnect: %s' % close_code, extra={'user': self.user})
        for chan in list(self.channels_list.keys()): self.leave_channel(chan)
        for name,consumer in self.actives.items(): consumer.disconnect(close_code)

    @property
    def uid(self, user=None):
        if user: return user.uid if hasattr(user, 'uid') else user['hashnonymous']
        return self.user.uid if hasattr(self.user, 'uid') else self.user['hashnonymous']

    @property
    def id(self, user=None):
        if user: return user.id if hasattr(user, 'id') else user.session_key
        if user: return self.user.id if hasattr(self.user, 'id') else self.user.session_key

    @property
    def user_representation(self):
        return self.user.session_data['email'] if self.user._meta.model_name == 'session' and 'email' in self.user.session_data else str(self.user)            

    def get_user_obj(self, scope):
        return scope['user'] if getattr(scope['user'], 'id') else scope['session']

    def save_user_channel(self):
        if self.user._meta.model_name == 'user' and self.obj.channel != self.channel_name: self.obj.channel = self.channel_name
        else: self.obj['channel'] = self.channel_name
        self.obj.save()

    def connect_channel(self, _type, name, _id):
        channel = Channel.objects.get_or_create(channel_name=name)
        if not channel.channel_type: channel.channel_type = _type
        channel.connect_user(self.channel_name, self.user, self.id)
        self.channels_list[name] = channel

    def join_channel(self, _type, name):
        if name not in self.channels_list:
            logger.info('join channel: %s' % name, extra={'user': self.user})
            database_sync_to_async(self.connect_channel)(_type, name, self.id)
            async_to_sync(self.channel_layer.group_add)(name, self.channel_name)

    def disconnect_channel(self, _type, name, _id):
        channel = Channel.objects.get_or_create(channel_name=name)
        channel.disconnect_user(self.channel_name, self.user, self.id)
        del self.channels_list[name]

    def leave_channel(self, name):
        if name in self.channels_list:
            logger.info('leave room: %s' % name, extra={'user': self.user})
            database_sync_to_async(self.disconnect_channel)(_type, name, self.id)
            async_to_sync(self.channel_layer.group_discard)(name, self.channel_name)

    def historize_channel(self, name, event, datas):
        self.channels_list[name].historize(self.id, event, datas)

    def send_to_channel(self, name, event, datas={}, _from=None):
        datas.update({'type': 'send.event', 'dispatch': event, 'uid': str(self.uid)})
        if _from: datas['from'] = _from
        logger.info('send room: %s, event: %s, datas %s' % (name, event, str(datas)), extra={'user': self.user})
        database_sync_to_async(self.historize_channel)(name, event, datas)
        async_to_sync(self.channel_layer.group_send)(name, datas)

    def receive(self, text_data):
        logger.info('receive: %s'%text_data, extra={'user': self.user})
        text_data = json.loads(text_data)
        args = text_data.get('args', {})
        cmd = text_data.get('cmd').split('.')
        print(cmd)
        if cmd[0] in self.consumers:
            if cmd[0] not in self.actives:
                self.actives[cmd[0]] = self.consumers[cmd[0]](self)
            self.actives[cmd[0]].dispatch(cmd, args)
        else:
            self.send_event({'status': False, 'event': '.'.join(cmd)})

    def send_event(self, event):
        event['self'] = 'uid' in event and str(self.uid) == event['uid']
        logger.info('event: %s' % event, extra={'user': self.user})
        self.send(text_data=json.dumps(event))