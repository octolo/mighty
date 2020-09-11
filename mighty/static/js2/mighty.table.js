var MightyTableTools = function(options) {
    MightyTools.call(this, options);
    this._shortcuts = {shortcuts: "sc", hide: "hide",}
    this.shortcuts = ['hide',]
    this._templates.hide = "hide-";
    this._templates.hideipt = "hideipt-";
    this.columnshide = [];

    this.getShortcuts = function(config, position, column) {
        html = ""
        for (sc in this.shortcuts) {
            shortcut = this.shortcuts[sc];
            if (typeof this[shortcut + "button"] === 'function') html += this[shortcut + "button"](config, position, column);
        }
        return html;
    }

    this.enableShortcuts = function(config) {
        for (sc in this.shortcuts) {
            shortcut = this.shortcuts[sc];
            if (typeof this[shortcut + "init"] === 'function') html += this[shortcut + "init"](config);
            this.is(config, true, true);
        }
    }

    this.hideload = function() {
        var elems = document.getElementsByClassName(this._templates.hide + this.configs.hide.class);
        var self = this;
        var config = this.target.is("toshow");
        var id = this.target.hasOwnProperty('connect') ? this.target.connect +"-"+ config : config;
        for (var i = 0; i < elems.length; i += 1) {
            elems[i].innerHTML = "";
            var columns = this.target.configs[config]["columns"];
            for (column in columns) {
                var label = document.createElement('label');
                var ipt = document.createElement('input');
                var name = [id, this.target._tables.column, column].join('-');
                ipt.type = "checkbox";
                ipt.name = name;
                ipt.className = this._templates.hideipt + name;
                ipt.checked = true;
                this.target.addEvent('change', ipt, function(){
                    if (self.stateCheckbox(this) == 0) {
                        if (self.columnshide.indexOf(this.name) >= 0){
                            var columns = document.getElementsByClassName(this.name);
                            for (var i = 0; i < columns.length; i += 1) columns[i].style.display = '';
                            delete self.columnshide[self.columnshide.indexOf(this.name)];
                        }
                        var inputs = document.getElementsByClassName(self._templates.hideipt+this.name);
                        for (var i = 0; i < inputs.length; i += 1) self.nextCheckbox(inputs[i], 0); 
                    }else{
                        if (self.columnshide.indexOf(this.name) < 0) self.columnshide.push(this.name);
                        self.hidecolumns();
                    }
                });
                label.appendChild(ipt);
                label.appendChild(document.createTextNode(columns[column].header));
                elems[i].appendChild(label);
            }
        }
        this.hidecolumns();
    }

    this.hideinit = function(config) {
        var id = this.target.hasOwnProperty('connect') ? this.target.connect +"-"+ config : config;
        var elems = document.getElementsByClassName([id, this._shortcuts.shortcuts, this._shortcuts.hide].join('-'));
        var self = this;
        for (var i = 0; i < elems.length; i += 1) {
            this.addEvent("click", elems[i], function(e){
                var column = self.target.getColumn(this, config);
                if (self.columnshide.indexOf(column) < 0) self.columnshide.push(column);
                self.hidecolumns();
            });
        }
        //this.hidecolumns();
    }

    this.hidecolumns = function() {
        for (column in this.columnshide) {
            var columns = document.getElementsByClassName(this.columnshide[column]);
            for (var i = 0; i < columns.length; i += 1) columns[i].style.display = 'none';
            var inputs = document.getElementsByClassName(this._templates.hideipt+this.columnshide[column]);
            for (var i = 0; i < inputs.length; i += 1) this.nextCheckbox(inputs[i], 2); 
        }
    }

    this.hidebutton = function(config, position, column) {
        var id = this.target.hasOwnProperty('connect') ? this.target.connect +"-"+ config : config;
        var btn = '<button class="';
        input = [id, this.target._tables.column, position].join('-');
        if (!this.is(config)) {
            if (column.hasOwnProperty('ishide') && column.ishide) this.columnshide.push(input);
            else this._inputs.checkbox[this._templates.hideipt + input] = 1;
        }
        btn +=  [this._shortcuts.shortcuts, this._shortcuts.hide].join('-') + ' ' +[id, this._shortcuts.shortcuts, this._shortcuts.hide].join('-');
        btn += " "+input;
        btn += '">'+ this._icons.remove+'</button>';
        return btn;
    }

}

var MightyTable = function(options) {
    MightyCore.call(this, options);
    this._tables = { shortcuts: "shortcuts", table: "table", column: "column", header: "header", }

    this.getColumn = function(elem, config) {
        var id = this.hasOwnProperty('connect') ? this.connect +"-"+ config : config;
        var regex = new RegExp("("+[id, this._tables.column, '[0-9]+'].join('-')+")", "gi");
        var match = elem.className.match(regex);
        return match[0];
    }

    this.getShortcuts = function(config, position, column) {
        if (this.hasOwnProperty('tools')) return this.tools.getShortcuts(config, position, column);
        return "";
    }

    this.enableShortcuts = function(config) {
        if (this.hasOwnProperty('tools')) return this.tools.enableShortcuts(config);
    }

    this.getHeaders = function(config) {
        var columns = this.configs[config]["columns"];
        var html = "";
        var id = this.hasOwnProperty('connect') ? this.connect +"-"+ config : config;
        for (column in columns) {
            var shortcuts = this.getShortcuts(config, column, columns[column]);
            html += '<th class="'+[id, this._tables.column, column].join('-')+'">';
            html += '<div class="'+this._tables.shortcuts+' '+[id, this._tables.shortcuts].join('-')+'">'+ shortcuts +'</div>';
            html += '<div class="'+this._tables.header+' '+[id, this._tables.header].join('-')+'">'+ columns[column].header +'</div></th>';
        }
        return html;
    }

    this.getColumns = function(config) {
        var columns = this.configs[config]["columns"];
        var html = "";
        var id = this.hasOwnProperty('connect') ? this.connect +"-"+ config : config;
        for (column in columns) {
            if (columns[column].hasOwnProperty("template")) 
                html += '<td class="'+[id, this._tables.column, column].join('-')+'"><div class="data">'+columns[column].template+'</div></td>';
            else
                html += '<td class="'+[id, this._tables.column, column].join('-')+'"><div class="data">[['+columns[column].data+']]</div></td>';
        }
        return html;
    }

    this.show = function(what, change) {
        change = change === undefined ? false : true;
        what = what === undefined ? this.is("toshow") : what;
        this.log("debug", "show", what);
        if (this.is("toshow") == what) {
            this.dropAll(what);
            var headers = this.getHeaders(what);
            var columns = this.getColumns(what);
            var template = '<table id="'+[what, this._tables.table].join('-')+'" cellspacing="0" cellspadding="0">';
            template += "<thead>" + headers + "</thead><tbody>[[#each datas]]<tr>" + columns + "</tr>[[/each]]</tbody></table>";
            this.template(what, this.datas[what], template);
            this.enableShortcuts(what);
            this.reloadtools();
            if(!this.is("inittools")) { 
                this.is("inittools", true, true);
                this.loadtools();
            }
            this.end(what);
        } else if (change) {
            this.working = 0;
            this.is("toshow", what, true);
            this.process(0);
        }
    }
}

var MightyTableAjax = function(options) {
    MightyAjax.call(this, options);
    MightyTable.call(this, options);
}