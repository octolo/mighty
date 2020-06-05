var MightyCommon = function(options) {
    MightyCore.call(this, options);
    this.working = 0;
    this.datas = {};
    this.connection_name = false;
    this.lists = {filters: [], excludes: []};
    this.form = {search: null, searchex: null, filters: null, excludes: null};

    this.delay = function(config, ms, action) {
        action = action === undefined ? false : action;
        ms = ms === undefined ? this.msdelay : ms;
        this.log("debug", "delay", [config, ms, action]);
        clearTimeout(this._timer[config]);
        var self = this;
        this._timer[config] = setTimeout(function() { self.do(config, action); }, ms || 0);
    }

    this.process = function(ms, action) {
        if(!this.working){
            this.working = Object.keys(this.configs).length;
            action = action === undefined ? false : action;
            ms = ms === undefined ? this.msdelay : ms;
            this.log("debug", "process", [this.working, ms, action]);
            for (config in this.configs) this.processconfig(config, ms, action);
            if(!this.is("init")) { this.is("init", true, true); }
        }
    }

    this.processconfig = function(config, ms, action) {
        if(!this.is("prepared")) { this.prepare(config); }
        this.is("blocked", true, true);
        this.loader(true);
        action = action === undefined ? false : action;
        ms = ms === undefined ? this.msdelay : ms;
        this.log("debug", "processconfig", [config, this.working, ms, action]);
        this.delay(config, ms, action);
    }

    this.dropAll = function(except) {
        except = except === undefined ? false : except;
        this.log("debug", "dropAll", except);
        if (this.hasOwnProperty('connect')){
            document.getElementById(this._templates.render + this.connect).innerHTML = "";
        } else {
            for (config in this.configs) {
                if (!except || except != config) {
                    document.getElementById(this._templates.render + config).innerHTML = "";
                }
            }
        }
    }

    this.template = function(config, datas, template) {
        template = template === undefined ? false : template;
        this.log("debug", "template", template);
        config = config === undefined ? this.is("toshow") : config;
        datas = datas === undefined ? null : datas;
        this.log("debug", "template", [config, datas]);
        if (template) var source = template.replace(/\[\[/g, '{{').replace(/\]\]/g, '}}');
        else var source = this.getElement(config, "template");
        template = Handlebars.compile(source);
        var html = template({datas: datas});
        var id = this.hasOwnProperty('connect') ? this.connect : config;
        this.getElement(id, "render").innerHTML = html;
    }

    this.show = function(what) {
        what = what === undefined ? this.is("toshow") : what;
        this.log("debug", "show", what);
        if (this.is("toshow") == what) {
            this.dropAll(what);
            this.template(what, this.datas[what]);
            this.reloadtools();
            if(!this.is("inittools")) { 
                this.is("inittools", true, true);
                this.loadtools();
            }
            this.end(what);
        }
    }

    this.forceend = function() {
        this.working = 0;
    }
    
    this.loader = function(state) {
        var loader = this.is('loader');
        if (loader) {
            elems = document.getElementsByClassName(loader);
            for (var i = 0; i < elems.length; i += 1) {
                elems[i].style.display = state ? "block" : "none";
            }
        }
    }

    this.loadtools = function() {
        if (this.hasOwnProperty("tools")) this.tools.load();
    }

    this.reloadtools = function() {
        if (this.hasOwnProperty("tools")) this.tools.reload();
    }

    this.end = function(what) {
        var self = this;
        if (this.working > 0) {
            setTimeout(function() { self.end(what); }, 500);
        }else{
            this.is("blocked", false, true);
            this.loader(false);
            this.doend(what);
        }
    }

    this.prepare = function(config) {
        this.is("prepared", true, true); 
    }

    this.do = function(config, action) {
        action = action === undefined ? false : action;
        this.working--;
        if (config == this.is("toshow")) this.show(config);
    }

    this.doend = function(config) {
        this.log("debug", "doend", config);
    }
}