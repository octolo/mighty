function change_style(style, callback) {
    callback = callback === undefined ? false : callback;
    var xhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
    xhttp.open('GET', '/accounts/style/'+style+'/');
    xhttp.timeout = 500;
    xhttp.onload = function(event) {
        if (callback) {
            callback(xhttp.reponse);
        } else {
            data = JSON.parse(xhttp.response); 
            document.getElementsByTagName('body')[0].className = data.style;
        }
    }
    xhttp.send();
}

function add_css(href, callback){
    for(var i = 0; i < document.styleSheets.length; i++){
        if(document.styleSheets[i].href == href){ return; }
    }
    var head  = document.getElementsByTagName('head')[0];
    var link  = document.createElement('link');
    link.rel  = 'stylesheet';
    link.type = 'text/css';
    link.href = href;
    if (callback) { link.onload = function() { callback() } }
    head.appendChild(link);
}

function get_widget(widget, callback) {
    var xhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
    xhttp.open('GET', '/widgets/'+widget+'/');
    xhttp.timeout = 500;
    xhttp.onload = function(event) { callback(xhttp.response); }
    xhttp.send();
}

function Mconfig(options) {
    this.protocol = location.protocol + '//' + location.host + location.pathname;
    this.location = window.location.host;
    this.loglvl = { debug: "#FFFFFF", info: "#7bd5ff", warn: "#FF7F5D", error: "#FF3232" };
    this.options = options === undefined ? {} : options;
    for(var option in this.options) { this[option] = this.options[option]; }
    this.debug = this.debug  === undefined ? 'warn' : this.debug;

    this.randdarkcolor = function() {
        var lum = -0.25;
        var hex = String('#' + Math.random().toString(16).slice(2, 8).toUpperCase()).replace(/[^0-9a-f]/gi, '');
        if (hex.length < 6) { hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]; }
        var rgb = "#", c, i;
        for (i = 0; i < 3; i++) {
            c = parseInt(hex.substr(i * 2, 2), 16);
            c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
            rgb += ("00" + c).substr(c.length);
        }
        return rgb;
    }

    this.log = function(lvl, msg, array) {
        array = array === undefined ? null : array;
        if (!this.hasOwnProperty("logbg")) { this.logbg = this.randdarkcolor();  }
        if (this.debug) {
            console.log("%c " + Date.now().toString() + ": " + lvl + " | " + msg, "background: " + this.logbg + "; color: " + this.loglvl[lvl]);
            if (array) { console[lvl](array); }
        }
    }
}

var Mwebsocket = function(options) {
    Mconfig.call(this, options);
    this.url = 'ws://'+this.location+'/mighty.ws'
    
    this.ws = function() {
        if (this._ws === undefined) {
            this._ws = new WebSocket(this.url);
            var self = this;
            this._ws.onmessage = function(e) { self.receive(e); }
            this._ws.onclose = function(e) { self.disconnect(e); }
        }
        return this._ws;
    }

    this.send = function(cmd, args) {
        args = args === undefined ? {} : args;
        if (cmd !== undefined) {
            if (this._ws.readyState === 1) {
                this._ws.send(JSON.stringify({'cmd': cmd, 'args': args}));
            } else {
                var self = this;
                setTimeout(function () { self.send(cmd, args); }, 100);
            }
        }
    }

    this.receive = function(e) {
        const data = JSON.parse(e.data)
        if (data.message === undefined) {
            alert(data.error);
        } else {
            alert(data.message);
        }
    }

    this.disconnect = function(e) {
        delete this._ws;
        this._ws = this.ws();
    }

    this.chat_support = function(id) {
        get_widget('chat.html', function(widget){
            document.getElementById(id).innerHTML += widget;
        });
    }
}