var MightyTableTools = function(options) {
    MightyTools.call(this, options);
    this._shortcuts = {shortcuts: "sc", hide: "hide",}
    this.hidecolumns = [];

    this.reloadhide = function(config) {
        for (var i = 0; i < self.hidecolumns.length; i += 1) {
            var columns = document.getElementsByClassName(self.hidecolumns[i]);
            for (var i = 0; i < columns.length; i += 1) {
                columns[i].style.display = 'none';
            }
        }
    }

    this.hide = function(config) {
        var elems = document.getElementsByClassName([config, this._shortcuts.shortcuts, this._shortcuts.hide].join('-'));
        var self = this;
        for (var i = 0; i < elems.length; i += 1) {
            this.addEvent("click", elems[i], function(e){
                var column = self.target.getColumn(this, config);
                if (self.hidecolumns.indexOf(column) < 0) self.hidecolumns.push(column);
                var columns = document.getElementsByClassName(column);
                for (var i = 0; i < columns.length; i += 1) columns[i].style.display = 'none';
            });
        }
    }

    this.hideButton = function(config, column) {
        var btn = '<button class="';
        btn += [config, this._shortcuts.shortcuts, this._shortcuts.hide].join('-');
        btn += " "+[config, this.target._tables.column, column].join('-');
        btn += '">hide</button>';
        return btn;
    }

    this.hideColumn = function(config, column, state) {
        state = state === undefined ? false : state;
        document.getElementsByClassName(this.target._tables.column + column).style.display = state ? "none" : "block";
    }
}

var MightyTable = function(options) {
    MightyCore.call(this, options);
    this._tables = { shortcuts: "shortcuts", table: "table", column: "column", header: "header", }

    this.getColumn = function(elem, config) {
        var regex = new RegExp("("+[config, this._tables.column, '[0-9]+'].join('-')+")", "gi");
        var match = elem.className.match(regex);
        return match[0];
    }

    this.getShortcuts = function(config, column) {
        html = "";
        if (this.hasOwnProperty('tools')) {
            if (this.tools.configs.hasOwnProperty('hide')) {
                html += this.tools.hideButton(config, column);
            }
        }
        return html;
    }

    this.getHeaders = function(config) {
        var columns = this.configs[config]["columns"];
        var html = "";
        for (column in columns) {
            var shortcuts = this.getShortcuts(config, column);
            html += '<th class="'+[config, this._tables.column, column].join('-')+'">';
            html += '<div class="'+[config, this._tables.shortcuts].join('-')+'">'+ shortcuts +'</div>';
            html += '<div class="'+[config, this._tables.header].join('-')+'">'+ columns[column].header +'</div></th>';
        }
        return html;
    }

    this.getColumns = function(config) {
        var columns = this.configs[config]["columns"];
        var html = "";
        for (column in columns) {
            if (columns[column].hasOwnProperty("template")) 
                html += '<td class="'+[config, this._tables.column, column].join('-')+'">'+columns[column].template+'</td>';
            else
                html += '<td class="'+[config, this._tables.column, column].join('-')+'">[['+columns[column].data+']]</td>';
        }
        return html;
    }

    this.show = function(what) {
        what = what === undefined ? this.is("toshow") : what;
        this.log("debug", "show", what);
        this.is("toshow", what, true);
        this.dropAll(what);
        //for (config in this.configs) this.getElement(config, "render").style.display = config == what ? "block" : "none";
        var headers = this.getHeaders(what);
        var columns = this.getColumns(what);
        var template = "<table id="+[config, this._tables.table].join('-')+">";
        template += "<thead>" + headers + "</thead><tbody>[[#each datas]]<tr>" + columns + "</tr>[[/each]]</tbody></table>";
        this.template(what, this.datas[what], template);
        if (this.hasOwnProperty('tools')){
            this.tools.hide(what);
            this.tools.reloadhide(what);
        }
        this.end(what);
    }
}

var MightyTableAjax = function(options) {
    MightyAjax.call(this, options);
    MightyTable.call(this, options);
}