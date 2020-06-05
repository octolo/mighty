function Mcommon(url, options) {
    Mconfig.call(this, url, options);
    this.working = 26;

    this.randdarkcolor = function() {
        var lum = -0.25;
        var hex = String('#' + Math.random().toString(16).slice(2, 8).toUpperCase()).replace(/[^0-9a-f]/gi, '');
        if (hex.length < 6) {
            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
        }
        var rgb = "#",
            c, i;
        for (i = 0; i < 3; i++) {
            c = parseInt(hex.substr(i * 2, 2), 16);
            c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
            rgb += ("00" + c).substr(c.length);
        }
        return rgb;
    }

    this.log = function(lvl, msg, array) {
        array = array === undefined ? null : array;
        if (!this.hasOwnProperty("logbg")) {
            this.logbg = this.randdarkcolor();
        }
        if (this.debug) {
            console.log("%c " + Date.now().toString() + ": " + lvl + " | " + msg, "background: " + this.logbg + "; color: " + this.colors[lvl]);
            if (array) {
                console[lvl](array);
            }
        }
    }

    this.delay = function(config, ms, action) {
        this.log("debug", "delay", [config, ms, action]);
        delete this.questions.is["blocked"];
        clearTimeout(this.timer[config]);
        var self = this;
        this.timer[config] = setTimeout(function() {
            self.xhr(config, action);
        }, ms || 0);
    }

    this.last = function(config, what, like) {
        this.log("debug", "last", [config, what, like]);
        if (like === undefined) {
            this.questions.lasts[config][what.key] = what.value;
        } else {
            return (this.questions.lasts[config].hasOwnProperty(what) && this.questions.lasts[config][what] === like) ? false : true;
        }
    }

    this.i = function(what, i) {
        this.log("debug", "i", [what, i]);
        i = i === undefined ? 0 : i;
        if (this.questions.i.hasOwnProperty(what)) {
            i = this.questions.i[what];
        } else {
            this.questions.i[what] = 0;
        }
        this.questions.i[what]++;
        return i;
    }

    this.is = function(what, status, newstatus) {
        this.log("debug", "is", [what, status, newstatus]);
        status = status === undefined ? false : status;
        newstatus = newstatus === undefined ? false : newstatus;
        if (!this.questions.is.hasOwnProperty(what)) {
            this.questions.is[what] = status;
        }
        if (newstatus) {
            this.questions.is[what] = status;
        }
        return this.questions.is[what];
    }

    this.add = function(config, key, value) {
        this.log("debug", "add", [config, key, value]);
        value = value === undefined ? {} : value;
        this.log("debug", "add - config: " + config + ", key: " + key, config);
        if (!this.is("showable")) {
            this.is("showable", config, true);
        }
        if (!this.config.hasOwnProperty(config)) {
            this.questions.lasts[config] = {};
            this.config[config] = {};
        }
        this.config[config][key] = value;
    }

    this.serialize = function(datas, merge) {
        this.log("debug", "serialize", [datas, merge]);
        var str = [];
        var form_datas = {};
        for (var p in merge) {
            if (merge[p]) form_datas[p] = merge[p];
        }
        for (var p in datas) {
            if (datas[p]) form_datas[p] = form_datas.hasOwnProperty(p) ? datas[p] + " " + form_datas[p] : datas[p];
        }
        for (var p in form_datas) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(form_datas[p]));
        }
        return str.join("&");
    }

    this.addEvent = function(evnt, elem, func) {
        this.log("debug", "addEvent", [evnt, elem, func]);
        if (elem.addEventListener) {
            elem.addEventListener(evnt, func, false);
        } else if (elem.attachEvent) {
            elem.attachEvent("on" + evnt, func);
        } else {
            elem["on" + evnt] = func;
        }
    }

    this.xhr = function(config, action) {
        this.log("debug", "xhr", [config, action]);
        if (this.config[config].xhttp) { this.config[config].xhttp.abort(); }
        var self = this;
        var url = this.config[config].hasOwnProperty("url") ? this.config[config]["url"] : this.url;
        this.form.filters = this.lists.filters.length ? this.lists.filters.join(" ") : null;
        this.form.excludes = this.lists.excludes.length ? this.lists.excludes.join(" ") : null;
        var datas = this.config[config].hasOwnProperty("datas") ? this.serialize(this.form, this.config[config]["datas"]) : this.serialize(this.form);
        var method = this.config[config].hasOwnProperty("method") ? this.config[config]["method"] : this.method;
        var datatype = this.config[config].hasOwnProperty("datatype") ? this.config[config]["datatype"] : this.datatype;
        this.config[config].xhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
        if (action == "next") {
            url = this.config[config]["response"][this.ajax.next];
        } else if (action == "previous" && this.config[config]["response"][this.ajax.previous]) {
            url = this.config[config]["response"][this.ajax.previous];
        } else {
            url = url + "?" + datas;
        }
        if (url.substr(0, this.protocol.length) != this.protocol) url = url.replace("http", "https");
        if (this.last(config, "url", url) || this.last(config, "datas", datas)) {
            this.last(config, { key: "url", value: url });
            this.last(config, { key: "datas", value: datas });
            this.config[config].lastdatas = datas;
            this.config[config].xhttp.open(method, url, true);
            this.config[config].xhttp.timeout = this.config[config].hasOwnProperty("method") ? this.config[config]["timeout"] : this.timeout;
            this.config[config].xhttp.onprogress = function() {
                self.log("log", "onprogress - url: " + url + ", method: " + method + ", config: " + config);
            };
            this.config[config].xhttp.onload = function(e) {
                self.log("log", "onload - url: " + url + ", datatype: " + datatype, self.config[config].xhttp.response);
                if (datatype == "json") self.config[config]["response"] = JSON.parse(self.config[config].xhttp.response);
                if (self.is("showable") == config){
                    self.show(config);
                }else{
                    self.protect(config, false);
                }
                self.config[config].xhttp = null;
            };
            this.config[config].xhttp.onabort = function(e) {
                self.log("error", "onabort - url: " + url + ", method: " + method + ", config: " + config, e);
                self.protect(config, false);
                self.config[config].xhttp = null;
            };
            this.config[config].xhttp.onerror = function(e) {
                self.log("error", "onerror - url: " + url + ", method: " + method + ", config: " + config, e);
                self.protect(config, false);
                self.config[config].xhttp = null;
            };
            this.config[config].xhttp.send(datas);
        } else {
            this.protect(config, false);
        }
    }

    this.protect = function(config, status) {
        this.log("debug", "protect", [config, status]);
        status = status === undefined ? true : status;
        var protector = document.getElementById(config + "-protector"); 
        if (status) { 
            if (protector) { protector.style.display = "block"; }
        } else { 
            if (protector) { protector.style.display = "none"; }
            this.working--;
        }
    }

    this.processconfig = function(config, ms, action) {
        this.working = this.working ? this.working : 1;
        this.protect(config);
        this.log("debug", "processconfig", [config, ms, action]);
        action = action === undefined ? false : action;
        ms = ms === undefined ? this.msdelay : ms;
        this.delay(config, ms, action);
    }

    this.h_init = function() {  }
    this.process = function(ms, action) {
        this.working = Object.keys(this.config).length;
        this.log("debug", "processconfig", [ms, action]);
        action = action === undefined ? false : action;
        ms = ms === undefined ? this.msdelay : ms;
        if(!this.is("firstevents")){
            this.searchable(this.is("searchable"));
            this.filterable(this.is("filterable"));
            this.is("firstevents", true, true);
        }
        for (config in this.config) {
            
            this.processconfig(config, ms, action);
        }
        if (!this.is("init")) {
            this.events();
            this.h_init();
            this.is("init", true, true);
        }
    }

    this.top = function() {
        this.log("debug", "top");
        if (this.is("top")) {
            document.getElementById(this.is("top")).scrollIntoView();
        }
    }

    this.events = function() {
        this.log("debug", "events");
        this.nextable(this.is("nextable"));
        this.previousable(this.is("previousable"));
    }

    this.searchable = function(searchable) {
        this.log("debug", "searchable", [searchable]);
        var self = this;
        if (searchable) {
            var form = document.getElementById(searchable);
            this.addEvent('submit', form, function(event) { event.preventDefault(); });
            this.addEvent('keyup', form.elements['search'], function(event) {
                self.top();
                self.form.search = this.value;
                if (this.value) {
                    self.add_tag(self.translation.search + ": " + this.value, "search", function(){
                        document.getElementById(searchable).elements['search'].value = "";
                        self.form.search = form.elements['search'].value;
                        self.process(self.msdelay, "search");
                    });
                } else {
                    self.remove_tag("search");
                }
                self.process(self.msdelay, "search");
            });
            this.form.search = form.elements['search'].value;
        }
    }

    this.exportable = function(exportable) {
        this.log("debug", "exportable", [exportable]);
        for (config in this.config) {
            if (this.config[config]["export"]) {
                alert(document.getElementById(this.config[config]["export"]).href);
            }
        }
    }

    this.dropAll = function(except) {
        except = except === undefined ? false : except;
        for (config in this.config) {
            if (!except || except != config) {
                this.drop(config);
            }
        }
    }

    this.drop = function(config){
        document.getElementById(config).innerHTML = "";
    }

    this.template = function(config, action) {
        action = action === undefined ? false : action;
        config = config === undefined ? this.is("showable") : config;
        console.log(this.config[config]["response"]);
        this.log("debug", "template", [config, response, action]);
        var response = this.config[config]["response"];
        var source = this.config[config].hasOwnProperty("template") ? this.config[config]["template"] : this.actions.template + config;
        this.log("debug", "template config: " + source);
        source = document.getElementById(source).innerHTML;
        source = source.replace(/\[\[/g, '{{');
        source = source.replace(/\]\]/g, '}}');
        var template = Handlebars.compile(source);

        if (response.hasOwnProperty(this.ajax.results)) {
            var results = response[this.ajax.results];
            var html = template({
                config: config,
                "datas": results,
                "options": response
            });
        } else {
            var html = template({
                config: config,
                "datas": response
            });
        }
        document.getElementById(config).innerHTML = html;
        this.protect(config, false);
        this.after(config, response, action);
        delete this.questions.is["blocked"];
    }

    this.h_after = function(cofig, response, action, datas) {}
    this.after = function(config, response, action,) {
        this.log("debug", "after", [config, response, action]);
        action = action === undefined ? false : action;
        this.next(this.is("nextable"), response, true);
        this.previous(this.is("previousable"), response, true);
        this.h_after(config, response, action, this.config[config].lastdatas);
    }

    this.nextable = function(next) {
        this.log("debug", "nextable", [next]);
        next = next === undefined ? false : next;
        if (next) {
            var self = this;
            var elems = document.getElementsByClassName(next);
            for (var i = 0; i < elems.length; i += 1) {
                this.addEvent("click", elems[i], function(e) {
                    self.next(next);
                    self.top();
                });
            }
        }
    }

    this.next = function(next, response, show) {
        this.log("debug", "next", [next, response, show]);
        next = next === undefined ? false : next;
        response = response === undefined ? false : response;
        show = show === undefined ? false : show;
        if (show) {
            if (response.hasOwnProperty(this.ajax.next) && response[this.ajax.next]) {
                var elems = document.getElementsByClassName(next);
                for (var i = 0; i < elems.length; i += 1) {
                    elems[i].style.display = "block";
                }
            } else {
                var elems = document.getElementsByClassName(next);
                for (var i = 0; i < elems.length; i += 1) {
                    elems[i].style.display = "none";
                }
            }
        } else {
            if (next) {
                this.processconfig(this.is("showable"), 0, "next");
            }
        }
    }

    this.previousable = function(previous) {
        this.log("debug", "previousable", [previous]);
        previous = previous === undefined ? false : previous;
        if (previous) {
            var self = this;
            var elems = document.getElementsByClassName(previous);
            for (var i = 0; i < elems.length; i += 1) {
                this.addEvent("click", elems[i], function(e) {
                    self.previous(previous);
                    self.top();
                });
            }
        }
    }

    this.previous = function(previous, response, show) {
        this.log("debug", "previous", [previous, response, show]);
        previous = previous === undefined ? false : previous;
        response = response === undefined ? false : response;
        show = show === undefined ? false : show;
        if (show) {
            if (response.hasOwnProperty(this.ajax.previous) && response[this.ajax.previous]) {
                var elems = document.getElementsByClassName(previous);
                for (var i = 0; i < elems.length; i += 1) {
                    elems[i].style.display = "block";
                }
            } else {
                var elems = document.getElementsByClassName(previous);
                for (var i = 0; i < elems.length; i += 1) {
                    elems[i].style.display = "none";
                }
            }
        } else {
            if (previous) {
                this.processconfig(this.is("showable"), 0, "previous");
            }
        }
    }

    this.show = function(what) {
        what = what=== undefined ? this.is("showable") : what;
        this.log("debug", "show", what);
        this.is("showable", what, true);
        this.dropAll(what);
        this.template(what);
        for (config in this.config) {
            document.getElementById(config).style.display = config == what ? "block" : "none";
            if (config == what) {
                this.counter(this.is("counter"), what);
                this.next(this.is("nextable"), this.config[what]["response"], true);
                this.previous(this.is("previousable"), this.config[what]["response"], true);
            }
        }
    }

    this.counter = function(id, config) {
        this.log("debug", "counter", [id, config]);
        id = id === undefined ? 0 : id;
        config = config === undefined ? 0 : config;
        if (id && config) {
            if ("response" in this.config[config] && this.ajax.count in this.config[config]["response"]) {
                var count = this.config[config]["response"][this.ajax.count];
                var results = count > 1 ? this.translation.results : this.translation.result;
                document.getElementById(id).innerHTML = count + " " + results;
            }
        }
    }

    this.stateInput = function(input) {
        this.log("debug", "stateInput", input);
        if (input.type == "checkbox") {
            return this.stateCheckbox(input);
        }
        return 0;
    }

    this.stateCheckbox = function(input) {
        this.log("debug", "stateCheckbox", input);
        if (this.inputs[input.type].hasOwnProperty(input.id)) {
            return this.inputs[input.type][input.id].state;
        } else {
            if (input.indeterminate) {
                return 2;
            } else if (input.checked) {
                return 1;
            }
        }
        return 0;
    }

    this.nextInput = function(input, force) {
        this.log("debug", "nextInput", input);
        for (list in this.lists) {
            if (this.lists[list].indexOf(input.value) != -1) {
                this.lists[list].splice(this.lists[list].indexOf(input.value), 1);
            }
        }
        if (input.type == "checkbox") {
            return this.nextCheckbox(input, force);
        }
    }

    this.nextCheckbox = function(input, force) {
        this.log("debug", "nextCheckbox", input);
        var current = force !== undefined ? force : this.inputs[input.type][input.id].state;
        if (current == 0) {
            input.indeterminate = false;
            input.checked = true;
            this.inputs[input.type][input.id].state = 1;
            return 1;
        } else if (current == 1) {
            input.checked = false;
            input.indeterminate = true;
            this.inputs[input.type][input.id].state = 2;
            return 2;
        }
        input.checked = false;
        input.indeterminate = false;
        this.inputs[input.type][input.id].state = 0;
        return 0;
    }

    this.addEventInput = function(input) {
        this.log("debug", "addEventInput", input);
        if (input.type == "checkbox") {
            return this.addEventCheckbox(input);
        }
    }

    this.addEventCheckbox = function(input) {
        this.log("debug", "addEventCheckbox", input);
        var self = this;
        var state = this.stateInput(input);
        if (state) {
            if (state == 1) {
                self.add_tag(self.icons.checked + " " + input.title, input.id, function(){
                    self.nextInput(input, 2);
                    self.process(self.msdelay, "checkbox");
                });
                self.lists.filters.push(input.value);
            } else if (state == 2) {
                self.add_tag(self.icons.indeterminate + " " + input.title, input.id, function(){
                    self.nextInput(input, 2);
                    self.process(self.msdelay, "checkbox");
                });
                self.lists.excludes.push(input.value);
            }
        }
        this.addEvent('click', input, function(e) {
            var input = this;
            var state = self.nextInput(this);
            if (state == 1) {
                self.add_tag(self.icons.checked + this.title, this.id, function(){
                    self.nextInput(input, 2);
                    self.process(self.msdelay, "checkbox");
                });
                self.lists.filters.push(input.value);
            } else if (state == 2) {
                self.add_tag(self.icons.indeterminate + " " + this.title, this.id, function(){
                    self.nextInput(input, 2);
                    self.process(self.msdelay, "checkbox");
                });
                self.lists.excludes.push(input.value);
            } else {
                self.remove_tag(this.id);
            }
            self.process(self.msdelay, "checkbox");
        });
    }

    this.filterable = function(filters) {
        this.log("debug", "filterable", filters);
        if (filters) {
            var allfilters = document.getElementsByClassName(filters);
            for (var f in allfilters) {
                var input = allfilters[f];
                if (this.inputs.hasOwnProperty(input.type)) {
                    this.inputs[input.type][input.id] = {
                        value: input.value,
                        state: this.stateInput(input)
                    };
                    this.addEventInput(input);
                }
            }
        }
    }

    this.add_tag = function(value, id, action) {
        if(this.is("taggable")) {
            id = this.is("taggable") + "-" + id;
            var button = document.getElementById(id);
            if (!button) {
                button = document.createElement('button');
                button.id = id;
                document.getElementById(this.is("taggable")).appendChild(button);
                this.addEvent("click", button, function(){
                    action();
                    this.remove();
                });
            }
            button.innerHTML = value + " | " + this.icons.remove;
        }
    }

    this.remove_tag = function(id) {
        document.getElementById(this.is("taggable") + "-" + id).remove();
    }
}