var MightyBasic = function(options) {
    MightyCore.call(this, options);
    this.working = 26;
    this.datas = {};
    this.connection_name = false;
    this.form = {search: null, searchex: null, filters: null, excludes: null};

    this.delay = function(config, ms, action) {
        action = action === undefined ? false : action;
        ms = ms === undefined ? this.msdelay : ms;
        this.log("debug", "delay", [config, ms, action]);
        clearTimeout(this._timer[config]);
        var self = this;
        this._timer[config] = setTimeout(function() { self.do(config, action); }, ms || 0);
    }

    this.processconfig = function(config, ms, action) {
        this.is("blocked", true, true);
        this.loader(true);
        this.working = this.working ? this.working : 1;
        console.log(this.working);
        action = action === undefined ? false : action;
        ms = ms === undefined ? this.msdelay : ms;
        this.log("debug", "processconfig", [config, this.working, ms, action]);
        this.delay(config, ms, action);
    }

    this.process = function(ms, action) {
        this.working = Object.keys(this.configs).length;
        action = action === undefined ? false : action;
        ms = ms === undefined ? this.msdelay : ms;
        this.log("debug", "process", [this.working, ms, action]);
        for (config in this.configs) this.processconfig(config, ms, action);
    }

    this.drop = function(config){
        this.log("debug", "drop", config);
        document.getElementById(this._templates.render + config).innerHTML = ""; 
    }

    this.dropAll = function(except) {
        except = except === undefined ? false : except;
        this.log("debug", "dropAll", except);
        for (config in this.configs) if (!except || except != config) this.drop(config);
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
        this.getElement(config, "render").innerHTML = html;
    }

    this.show = function(what) {
        what = what === undefined ? this.is("toshow") : what;
        this.log("debug", "show", what);
        this.is("toshow", what, true);
        this.dropAll(what);
        //for (config in this.configs) this.getElement(config, "render").style.display = config == what ? "block" : "none";
        this.template(what, this.datas[what]);
        this.end(what);
    }
    
    this.loader = function(state) {
        var elems = this.connection_name ? this.connection_name :  this.is("toshow");
        elems = document.getElementsByClassName(this._templates.loader + elems);
        for (var i = 0; i < elems.length; i += 1) {
            elems[i].style.display = state ? "block" : "none";
        }
    }

    this.reloadtools = function() {
        if (this.hasOwnProperty("tools")) this.tools.reload();
    }

    this.end = function(what) {
        var self = this;
        if (this.working) {
            setTimeout(function() { self.end(); }, 500);
        }else{
            this.is("blocked", false, true);
            this.loader();
            this.reloadtools();
        }
    }

    this.do = function(config, action) {
        action = action === undefined ? false : action;
        this.datas[config] = [1, 2, 3, 5];
        this.working--;
        if (config == this.is("toshow")) this.show(config);
    }
}