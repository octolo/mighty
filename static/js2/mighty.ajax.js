function MightyAjax(url, options) {
    MightyCommon.call(this, url, options);
    this.protocol = location.protocol;
    this.timeout = 20000;
    this.content = "json";
    this.sync = true;
    this.method = "GET";
    this.ajax = {count: "count", results: "results", result: "result", next: "next", previous: "previous"};

    this.serialize = function(datas, merge) {
        this.log("debug", "serialize", [datas, merge]);
        var str = [];
        var form_datas = {};
        for (var p in merge) if (merge[p]) form_datas[p] = merge[p];
        for (var p in datas) if (datas[p]) form_datas[p] = form_datas.hasOwnProperty(p) ? datas[p] + " " + form_datas[p] : datas[p];
        for (var p in form_datas) str.push(encodeURIComponent(p) + "=" + encodeURIComponent(form_datas[p]));
        return str.join("&");
    }

    this.getNextUrl = function(config, action, params) {
        if (this.nextable(config)) return this.configs[config].response[this.ajax.next];
        return false;
    }

    this.getPreviousUrl = function(config, action, params) {
        if (this.nextable(config)) return this.configs[config].response[this.ajax.previous];
        return false;
    }

    this.getUrl = function(config, action, params) {
        var action = action === undefined ? null : action;
        var params = params === undefined ? false : params;
        var url = this.configs[config].hasOwnProperty("url") ? this.configs[config].url : this.url;
        url += params ? "?" + params : "";
        this.log("debug", "getUrl", [action, url]);
        if (this.configs[config].hasOwnProperty("response")) {
            switch(action){
                case "next":
                    if (this.nextable(config)) url = this.configs[config].response[this.ajax.next];
                    break;
                case "previous":
                    if (this.previousable(config)) url = this.configs[config].response[this.ajax.previous];
                    break;
                default:
            }
        }
        return url;
    }

    this.ready = function(config, options, response) {
        if (options.content == "json") response = JSON.parse(response);
        this.configs[config].response = response;
        this.datas[config] = response.hasOwnProperty(this.ajax.results) ? response[this.ajax.results] : response;
        this.configs[config].xhttp = null;
        if (config == this.is("toshow")) this.show(config);
    }

    this.xhttp = function(options, callback){
        var url = options.hasOwnProperty("url") ? options.url : this.url;
        var sync = options.hasOwnProperty("sync") ? options.sync : this.sync;
        var method = options.hasOwnProperty("method") ? options.method : this.method;
        var content = options.hasOwnProperty("content") ? options.content : this.content;
        var config = options.hasOwnProperty("config") ? options.config : null;
        //var params = options.hasOwnProperty("params") ? "?" + options.params : "";
        var self = this;
        var xhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
        if (method == "GET") xhttp.open(method, url, sync);
        else xhttp.open(method, url, false);
        xhttp.timeout = this.configs[config].hasOwnProperty("timeout") ? this.config[config]["timeout"] : this.timeout;
        xhttp.onload = function(event) {
            self.log("debug", "onload - url: " + url + ", content: " + content, xhttp.response);
            self.working--;
            callback(options, xhttp.response);
        };
        xhttp.onabort = function(event) {
            self.log("debug", "onabort - url: " + url + ", method: " + method + ", config: " + config, event);
            self.configs[config].xhttp = null;
        };
        if (method == "POST") xhttp.send(params);
        else xhttp.send();
        return xhttp;
    }

    this.xhr = function(config, action) {
        if (this.configs[config].xhttp) { this.configs[config].xhttp.abort(); }
        var options = {config: config};
        this.form.filters = this.lists.filters.length ? this.lists.filters.join(" ") : null;
        this.form.excludes = this.lists.excludes.length ? this.lists.excludes.join(" ") : null;
        var params = this.configs[config].hasOwnProperty("params") ? this.serialize(this.form, this.configs[config]["params"]) : this.serialize(this.form);
        if (params) options.params = params;
        var method = this.configs[config].hasOwnProperty("method") ? this.configs[config].method : this.method;
        if (method) options.method = method;
        var content = this.configs[config].hasOwnProperty("content") ? this.configs[config].content : this.content;
        if (content) options.content = content;
        var url = options.url = this.getUrl(config, action, params);
        if (url.substr(0, this.protocol.length) != this.protocol) url = url.replace("http", "https");
        if (this.last(config, "url", url) && this.last(config, "params", params)) {
            this.show(config);
            this.working--;
        } else {
            this.last(config, "url", url);
            this.last(config, "params", params);
            var self = this;
            this.configs[config].xhttp = this.xhttp(options, function(options, response){ self.ready(config, options, response); });
        }
    }

    this.forceend = function(forced) {
        var forced = forced === undefined ? false : forced;
        for (config in this.configs) {
            if (this.configs[config].xhttp) { 
                this.configs[config].xhttp.abort(); 
                this.datas[config] = false;
                this._last[config] = {};
            }
        }
        if (forced) {
            if (this.configs[forced].xhttp) this.configs[forced].xhttp.abort(); 
            this.datas[forced] = false;
            this._last[forced] = {};
        }
        this.working = 0;
    }

    this.do = function(config, action) {
        this.xhr(config, action);
    }

    this.nextable = function(config) {
        return this.norpable(config, "next");
    }

    this.previousable = function(config) {
        return this.norpable(config, "previous");
    }

    this.norpable = function(config, norp) {
        if (this.configs[config].hasOwnProperty("response")
            && this.configs[config].response.hasOwnProperty(this.ajax[norp])
            && this.configs[config].response[this.ajax[norp]])
            return true;
        return false;
    }
}