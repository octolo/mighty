var Mchat = function(ws, options) {
    Mconfig.call(this, options);
    this.ws = ws;
    this.rooms = {}

    this.send = function(cmd, args){
        this.ws.send(JSON.stringify({'cmd': cmd, 'args': args}));
    }

    this.receive = function(event, data){
        switch(event) {
            case 'chat.message.support':
                var history = document.getElementById('chat-history-support');
                if (this.rooms['support'] != data.self) {
                    var div = document.createElement('div');
                    div.className = 'chat-history';
                    history.insertBefore(div, history.firstChild);
                }
                history = history.firstChild;
                var p = document.createElement('p');
                var who = data.self ? 'vous' : data.who;
                p.textContent = who + ': ' + data.message;
                history.appendChild(p, history.firstChild);
                this.rooms['support'] = data.self;
                break;
            case 'chat.connected.support':
                this.rooms['support'] = undefined;
                break;
            case 'chat.leave.support':
                delete this.rooms['support'];
                break;
            default:
                this.log('debug', data.event+':'+data.status);
                break;
        }
    }
}