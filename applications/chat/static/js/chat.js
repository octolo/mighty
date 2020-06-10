var Mchat = function(ws) {
    this.ws = ws;

    this.send = function(cmd, args){
        this.ws.send(JSON.stringify({'cmd': cmd, 'args': args}));
    }

    this.receive = function(action, data){
        switch(action) {
            case 'chat.message.support':
                document.getElementById('chat-support-history').innerHTML += '<p>' + data.message + '</p>';
                break;
        }
    }
}