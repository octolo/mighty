var MightyTools = function(target, options) {
    MightyCore.call(this, options);
    this.target = target;
    this.state = {searchex: false}
    this._templates = {search: "search-", searchex: "searchex-", next: "next-", previous: "previous-"};

    this.process = function() { for (tool in this.configs) if (typeof this[tool] === 'function') this[tool](); }
    this.reload = function() { 
        for (tool in this.configs) if (typeof this[tool + "load"] === 'function') this[tool + "load"](); 
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
                self.target.process(500);
                for (var i = 0; i < elems.length; i += 1) elems[i].value = this.value;
            });
        }
    }

    this.nextload = function() { this.norpload("next"); }
    this.next = function() { this.nextorprevious("next"); }

    this.previousload = function() { this.norpload("previous"); }
    this.previous = function() { this.nextorprevious("previous");}

    this.norpload = function(norp) {
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
                if (self.target.norpable(self.target.is("toshow"), norp))
                    self.target.processconfig(self.target.is("toshow"), 0, norp);
            });
        }
    }

}