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
            if cmd[1] == 'join':
                self.join(cmd[2], args)
            elif cmd[1] == 'message':
                self.send_message(cmd[2], args)
            elif cmd[1] == 'leave':
                self.leave(cmd[2], args)

    def join(self, to, args):
        room_name = '%s%s%s' % (self._ws.uid, self._ws.delimiter, to)
        self._ws.join_room(room_name)

    #def join_room(self, room_name, channel_name):
    #    if room_name not in self.rooms:
    #        async_to_sync(self._ws.channel_layer.group_add)(room_name, channel_name)
    #        self.rooms[room_name] = channel_name
    #        self._ws.send_event({'status': True, 'event': 'chat.connected.%s:chat' % room_name.split(self.delimiter)[1]})
    #        logger.info('room connection: %s' % room_name, extra={'user': self._ws.user})

    def leave(self, to, args):
        room_name = '%s%s%s' % (self._ws.uid, self._ws.delimiter, to)
        self._ws.leave_room(room_name)


    #def leave_room(self, room_name, channel_name):
    #    if room_name in self.rooms:
    #        print(room_name)
    #        self._ws.channel_layer.group_discard(room_name, channel_name)
    #        del self.rooms[room_name]
    #        self._ws.send_event({'status': True, 'event': 'chat.leave.%s:chat' % room_name.split(self.delimiter)[1]})


    def send_message(self, to, args):
        room_name = '%s%s%s' % (self._ws.uid, self._ws.delimiter, to)
        self._ws.send_to_room(room_name, 'chat.message.send:chat', {
            'event': 'chat.message.support:chat',
            'message': args['msg']
        })
        #if room_name in self.rooms:
        #    if 'msg' in args:
        #        async_to_sync(self._ws.channel_layer.group_send)(room_name, {
        #            'type': 'send.event',
        #            'event': 'chat.message.support:chat',
        #            'message': args['msg'],
        #            'uid': str(self._ws.uid)
        #        })
        #        self._ws.send_event({'status': True, 'event': 'chat.message.send:chat'})
        #    else:
        #        self._ws.send_event({'status': False, 'event': 'chat.message.send:chat'})
        #else:
        #    self._ws.send_event({'status': False, 'event': 'chat.connected.room:chat'})

    def disconnect(self, close_code):
        for room,channel in self.rooms.items():
            self.leave_room(room, channel)
