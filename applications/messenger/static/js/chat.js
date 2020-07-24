var Mchat = function(ws, options) {
    Mconfig.call(this, options);
    this.ws = ws;
    this.rooms = {}

    this.dispatch = function(cmd, args){
        switch(cmd[1]) {
            case 'join':
                cmd[2] == 'init' ? this.join_init(args.to) : this.join_accept(args.to);
                break;
            case 'leave':
                cmd[2] == 'init' ? this.leave_init(args.to) : this.leave_accept(args.to);
                break;
            case 'message':
                cmd[2] == 'send' ? this.message_send(args) : this.message_receive(args);
                break;
        }
    }

    this.join_init = function(to) {
        this.ws.send('chat.join.init', {'to': to});
    }

    this.join_accept = function(to) {
        this.ws.send('chat.join.accept', {'to': to});
    }

    this.leave_init = function(to) {
        this.ws.send('chat.leave.init', {'to': to});
    }

    this.leave_accept = function(to) {
        this.ws.send('chat.leave.accept', {'to': to});
    }

    this.message_send = function(args) {
        if (args['msg'] && args['to']) { this.ws.send('chat.message.send', {'to': args['to'], 'msg': args['msg']}); }
    }

    this.message_receive = function(args) {
        var history = document.getElementById('chat-history-' + args.chat);
        if (this.rooms[args.chat] != args.self) {
            var div = document.createElement('div');
            div.className = 'chat-history';
            history.insertBefore(div, history.firstChild);
        }
        history = history.firstChild;
        var p = document.createElement('p');
        var who = args.self ? 'vous' : args.from;
        p.textContent = who + ': ' + args.msg;
        history.appendChild(p, history.firstChild);
        this.rooms[args.chat] = args.self;
    }
}