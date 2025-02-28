# from asgiref.sync import async_to_sync
import logging

from mighty.consumers import Consumer

logger = logging.getLogger(__name__)


class ChatConsumer(Consumer):
    def __init__(self, ws):
        self.rooms = {}
        super().__init__(ws)

    def dispatch(self, cmd, args):
        if cmd[1] == 'message':
            if args['msg'] and args['to']:
                self.message_send(args['to'], args['msg']) if cmd[2] == 'send' else self.message_receive(args['to'], args['msg'])
        elif cmd[1] == 'join':
            self.join_init(args['to']) if cmd[2] == 'init' else self.join_accept(args['from'])
        elif cmd[1] == 'leave':
            self.leave_init(args['to'], args) if cmd[2] == 'init' else self.leave_accept(args['from'], args)

    def join(self, channel):
        self._ws.join_channel('chat', channel)

    def join_init(self, to):
        channel = '%s%s%s' % (self._ws.uid, self._ws.delimiter, to)
        self._ws.join_channel('chat', channel)

    def join_accept(self, to):
        channel = '%s%s%s' % (to, self._ws.delimiter, self._ws.uid)
        self._ws.join_channel('chat', channel)

    def leave_init(self, to):
        channel = '%s%s%s' % (self._ws.uid, self._ws.delimiter, to)
        self._ws.leave_channel(channel)

    def leave_accept(self, to):
        channel = '%s%s%s' % (to, self._ws.delimiter, self._ws.uid)
        self._ws.leave_channel(channel)

    def message_send(self, to, msg):
        channel = '%s%s%s' % (self._ws.uid, self._ws.delimiter, to)
        self._ws.send_to_channel(channel, 'chat.message.receive', {'chat': to, 'msg': msg, 'from': self._ws.user_representation})

    def message_receive(self, to, msg):
        channel = '%s%s%s' % (self._ws.uid, self._ws.delimiter, to)
        self._ws.send_to_channel(channel, 'chat.message.receive', {'chat': to, 'msg': msg})
