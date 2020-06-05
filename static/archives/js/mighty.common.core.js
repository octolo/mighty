var MightyCore = function(options) {
    for (option in options) this[option] = options[option];
    this._i = {};
    this._last = {};
    this._is = {};
    this._timer = {};
    this.configs = {};
    this._templates = {template: "template-", render: "render-", loader: "loader-",};
    this._lvl = {emerg: 0, alert: 1, crit: 2, error: 3, warning: 4, notice: 5, info: 6, debug: 7};

    this.log = function(lvl, msg, array) {
        array = array === undefined ? null : array;
        if (this.debug >= this._lvl[lvl]) {
            console.log(Date.now().toString() + ": " + lvl + " | " + msg);
            if (array) console.log(array);
        }
    }

    this.last = function(config, what, like) {
        this.log("debug", "last", [config, what, like]);
        if (like === undefined) {
            this._last[config][what.key] = what.value;
        }else{
            return (this._last[config].hasOwnProperty(what) && this._last[config][what] === like) ? false : true;
        }
        return this._last[config][what.key];
    }

    this.i = function(what, i) {
        i = i === undefined ? 0 : i;
        this.log("debug", "i", [what, i]);
        if (this.i.hasOwnProperty(what))vi = this._i[what];
        else this._i[what] = 0;
        this._i[what]++;
        return i;
    }

    this.is = function(what, status, newstatus) {
        oldstatus = this.is.hasOwnProperty(what) ? this._is[what] : false;
        status = status === undefined ? oldstatus : status;
        newstatus = newstatus === undefined ? false : newstatus;
        this.log("debug", "is", [what, status, newstatus]);
        if (newstatus) this._is[what] = status;
        return this._is[what];
    }

    this.add = function(config, key, value) {
        value = value === undefined ? false : value;
        this.log("debug", "add", [config, key, value]);
        if (!this.is("toshow")) this.is("toshow", config, true);
        if (!this.configs.hasOwnProperty(config)) {
            this._last[config] = {};
            this.configs[config] = {}; }
        if (value) this.configs[config][key] = value;
    }

    this.addEvent = function(evnt, elem, func) {
        this.log("debug", "addEvent", [evnt, elem, func]);
        if (elem.addEventListener) elem.addEventListener(evnt, func, false);
        else if (elem.attachEvent) elem.attachEvent("on" + evnt, func);
        else elem["on" + evnt] = func;
    }

    this.getElement = function(id, what){
        what = what === undefined ? null : this._templates[what];
        var tpl = what ? what + id : id;
        this.log("debug", "getElement", [id, what, tpl]);
        if (what == this._templates.template) {
            tpl = document.getElementById(tpl).innerHTML;
            tpl = tpl.replace(/\[\[/g, '{{');
            tpl = tpl.replace(/\]\]/g, '}}');
        }else{ tpl = document.getElementById(tpl); }
        return tpl;
    }
}