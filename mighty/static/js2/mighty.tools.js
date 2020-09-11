var MightyTools = function(target, options) {
    MightyCore.call(this, options);
    this.target = target;
    this.state = {searchex: false}
    this._templates = {
        count: "count-",
        search: "search-",
        searchex: "searchex-",
        next: "next-", 
        previous: "previous-",
        tag: "tag-",
        filter: "iptfilter-"
    };
    this._inputs = { checkbox: {}, radio: {} };
    this.tags_zone = "tagszone-";

    this.process = function() { for (tool in this.configs) if (typeof this[tool] === 'function') this[tool](); }
    this.load = function() { for (tool in this.configs) if (typeof this[tool + "load"] === 'function') this[tool + "load"](); }
    this.reload = function() { for (tool in this.configs) if (typeof this[tool + "reload"] === 'function') this[tool + "reload"](); }

    this.tagsload = function() { this.is("taggable", true, true);    }
    this.add_tag = function(value, id, action) {
        if(this.is("taggable")) {
            var self = this;
            var config = this.target.hasOwnProperty('connect') ? this.target.connect : this.target.is("toshow");
            var zone = this.tags_zone + config;
            id = this._templates.tag + config + "-" + id;
            var button = document.getElementById(id);
            if (!button) {
                button = document.createElement('button');
                button.id = id;
                document.getElementById(zone).appendChild(button);
                this.addEvent("click", button, function(){
                    action();
                    this.remove();
                });
            }
            button.innerHTML = value + " | " + this._icons.remove;
        }
    }

    this.remove_tag = function(id) {
        var config = this.target.hasOwnProperty('connect') ? this.target.connect  : this.target.is("toshow");
        id = this._templates.tag + config + "-" + id;
        document.getElementById(id).remove();
    }


    this.countreload = function() {
        if (this.target.configs[this.target.is("toshow")].hasOwnProperty("response")) {
            var elems = document.getElementsByClassName(this._templates.count + this.configs.count.class);
            for (var i = 0; i < elems.length; i += 1) {
                elems[i].innerHTML = this.target.configs[this.target.is("toshow")].response.count;
            }
            //this.ajax.count
                //var count = this.config[config]["response"][this.ajax.count];
            //var results = count > 1 ? this.translation.results : this.translation.result;
            //document.getElementById(id).innerHTML = count + " " + results;
        }
    }

    this.searchex = function() {
        var elems = document.getElementsByClassName(this._templates.searchex + this.configs.searchex.class);
        var self = this;
        for (var i = 0; i < elems.length; i += 1) {
            this.addEvent("change", elems[i], function(e){
                self.log("debug", "searchex", this.checked);
                for (var i = 0; i < elems.length; i += 1) elems[i].checked = this.checked;
                if (this.checked) {
                    self.target.form.searchex = self.target.form.search;
                    self.target.form.search = null;
                } else {
                    self.target.form.search = self.target.form.searchex;
                    self.target.form.searchex = null;
                }
                self.state.searchex = this.checked
                self.target.process(500);
            });
        }
    }
    
    this.search = function() {
        var elems = document.getElementsByClassName(this._templates.search + this.configs.search.class);
        var self = this;
        for (var i = 0; i < elems.length; i += 1) {
            this.addEvent("keyup", elems[i], function(e){
                if (self.state.searchex) self.target.form.searchex = this.value;
                else self.target.form.search = this.value;
                self.log("debug", "search", this.value);
                self.target.forceend();
                if (this.value) {
                    self.add_tag(self.translation.search + ": " + this.value, "search", function(){
                        var elems = document.getElementsByClassName(self._templates.search + self.configs.search.class);
                        for (var i = 0; i < elems.length; i += 1) { elems[i].value = ""; }
                        self.target.form.search = null;
                        self.target.form.searchex = null;
                        self.target.forceend();
                        self.target.process(self.msdelay, "search");
                    });
                } else {
                    self.remove_tag("search");
                }
                self.target.process(500);
                for (var i = 0; i < elems.length; i += 1) elems[i].value = this.value;
            });
        }
    }

    this.nextreload = function() {  this.norpreload("next"); }
    this.next = function() { this.nextorprevious("next"); }

    this.previousreload = function() { this.norpreload("previous"); }
    this.previous = function() { this.nextorprevious("previous");}

    this.norpreload = function(norp) {
        var state = this.target.norpable(this.target.is("toshow"), norp);
        var elems = document.getElementsByClassName(this._templates[norp] + this.configs[norp].class);    
        for (var i = 0; i < elems.length; i += 1) {
            if(!this.is("display" + norp + i)) {
                if (elems[i].style.display) this.is("display" + norp + i, elems[i].style.display, true);
                else this.is("display" + norp + i, "initial", true);
            }
            elems[i].style.display = state ? this.is("display" + norp + i) : "none";
        }    
    }

    this.nextorprevious = function(norp) {
        var elems = document.getElementsByClassName(this._templates[norp] + this.configs[norp].class);
        var self = this;
        for (var i = 0; i < elems.length; i += 1) {
            this.addEvent("click", elems[i], function(e){
                self.log("debug", norp);
                if (self.target.norpable(self.target.is("toshow"), norp)) {
                    self.target.working = 1;
                    self.target.processconfig(self.target.is("toshow"), 0, norp);
                }
            });
        }
    }

    this.filtersload = function(filters) {
        var config = this.target.hasOwnProperty('connect') ? this.target.connect : this.target.is("toshow");
        var elems = document.getElementsByClassName(this._templates.filter + config);
        for (var i = 0; i < elems.length; i += 1) {
            var input = elems[i];
            this._inputs[input.type][input.id] = this.stateInput(input);
            if(this._inputs[input.type][input.id] > 0) {
                this._inputs[input.type][input.id]--;
                this.CheckBoxClick(input);
            }
            this.addEventInput(input);
        }
    }

    this.nextCheckbox = function(input, force) {
        this.log("debug", "nextCheckbox", input);
        var key = input.id ? input.id : input.className;
        var current = force !== undefined ? force : this.stateCheckbox(input);
        if (current == 0) {
            input.indeterminate = false;
            input.checked = true;
            this._inputs[input.type][key] = 1;
            return 1;
        } else if (current == 1) {
            input.checked = false;
            input.indeterminate = true;
            this._inputs[input.type][key] = 2;
            return 2;
        }
        input.checked = false;
        input.indeterminate = false;
        this._inputs[input.type][key] = 0;
        return 0;
    }

    this.stateInput = function(input) {
        this.log("debug", "stateInput", input);
        if (input.type == "checkbox") {
            return this.stateCheckbox(input);
        }
        return 0;
    }

    this.nextInput = function(input, force) {
        this.log("debug", "nextInput", input);
        for (list in this.target.lists) {
            if (this.target.lists[list].indexOf(input.value) != -1) {
                this.target.lists[list].splice(this.target.lists[list].indexOf(input.value), 1);
            }
        }
        if (input.type == "checkbox") {
            return this.nextCheckbox(input, force);
        }
    }

    this.stateCheckbox = function(input) {
        var key = input.id ? input.id : input.className;
        if (this._inputs[input.type].hasOwnProperty(key)) {
            return this._inputs[input.type][key];
        } else {
            if (input.indeterminate) {
                return 2;
            } else if (input.checked) {
                return 1;
            }
        }
        return 0;
    }

    this.addEventInput = function(input) {
        this.log("debug", "addEventInput", input);
        if (input.type == "checkbox") {
            return this.addEventCheckbox(input);
        }
    }

    this.CheckBoxClick = function(input) {
        var self = this;
        var state = self.nextInput(input);
        if (state == 1) {
            this.add_tag(self._icons.checked + input.title, input.id, function(){
                self.nextInput(input, 2);
                self.target.forceend();
                self.target.process(self.msdelay, "checkbox");
            });
            this.target.lists.filters.push(input.value);
        }else if (state == 2) {
            this.add_tag(self._icons.indeterminate + input.title, input.id, function(){
                self.nextInput(input, 2);
                self.target.forceend();
                self.target.process(self.msdelay, "checkbox");
            });
            this.target.lists.excludes.push(input.value);
        }else {
            this.remove_tag(input.id);
        }
        this.target.forceend();
        this.target.process(this.msdelay, "checkbox");
    }

    this.addEventCheckbox = function(input) {
        var self = this;
        this.log("debug", "addEventCheckbox", input);
        this.addEvent('click', input, function(e) {
            self.CheckBoxClick(this);
        });
    }
}