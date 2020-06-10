from mighty.consumers import Consumer
from asgiref.sync import async_to_sync
import logging
logger = logging.getLogger(__name__)

class ChatConsumer(Consumer):
    def __init__(self, ws):
        self.rooms = {}
        super().__init__(ws)

    def default(self, cmd, args):
        cmd = cmd.split('.')
        if len(cmd) > 1:
            if cmd[1] == 'support':
                self.join_support()
            elif cmd[1] == 'message':
                self.send_message(cmd[2], args)

    def join_support(self):
        room_name = '%s__%s' % (self._ws.uid, 'support')
        self.join_room(room_name, self._ws.channel_name)

    def join_room(self, room_name, channel_name):
        if room_name not in self.rooms:
            async_to_sync(self._ws.channel_layer.group_add)(room_name, channel_name)
            self.rooms[room_name] = channel_name
            self._ws.send_event({'status': 'ok', 'event': 'join room'})
            logger.info('room connection: %s' % room_name, extra={'user': self._ws.user})

    def send_message(self, to, args):
        room_name = '%s__%s' % (self._ws.uid, to)
        if room_name in self.rooms:
            if 'msg' in args:
                async_to_sync(self._ws.channel_layer.group_send)(room_name, {
                    'type': 'send.event',
                    'action': 'chat.message.support:chat',
                    'message': args['msg']
                })
                self._ws.send_event({'status': 'ok', 'event': 'send message'})
            else:
                self._ws.send_event({'status': 'ko', 'event': 'send message'})
        else:
            self._ws.send_event({'status': 'ko', 'event': 'unknown room'})

    def leave_room(self, room_name, channel_name):
        if room_name in self.rooms:
            async_to_sync(self._ws.channel_layer.group_discard)(room_name, channel_name)
            del self.rooms[room_name]
            self._ws.send_event({'status': 'ok', 'event': 'leave room'})

    def disconnect(self, close_code):
        for room,channel in self.rooms.items():
            self.leave_room(room, channel)
