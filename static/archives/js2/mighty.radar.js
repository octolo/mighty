var MightyRadar = function(options) {
    MightyAjax.call(this, options);
    this.dropAll = function(except) {
        if (this.radartodraw) { 
            RGraph.SVG.clear(this.radartodraw.svg);
        }
    }
    this.ajax.results = false;
    this.addresults = false;
    this.usetables = true;
    this.axes = [];

    this.radartodraw = false;
    this.responsive = [
        {maxWidth: 300,  width: 200, height: 150, options: {textSize: 8}},
        {maxWidth: 400,  width: 300, height: 150, options: {textSize: 8}},
        {maxWidth: 600,  width: 400, height: 180, options: {textSize: 8}},
        {maxWidth: 1100, width: 500, height: 200, options: {textSize: 8}},
        {maxWidth: null, width: 500, height: 250, options: {textSize: 8}}
    ];
    this.colors = [];
    this.addfield = '';

    this.getLabels = function(config, results) {
        var results = results === undefined ? false : results;
        var labels = [];
        for (field in this.axes){
            if (results) {
                var results = [];
                for(data in this.datas) {
                    if (this.datas.hasOwnProperty(data) && this.datas[data].hasOwnProperty(field)) {
                        avg = this.datas[data][field];
                        max = this.axes[field].max;
                        if (avg && avg > 0) { results.push(Math.round(avg));} else { results.push(0); }
                    }
                }
                labels.push(this.axes[field].label + " (" + results.join('/') + ")");
            } else {
                labels.push(this.axes[field].label);
            }
        }
        return labels;
    }

    this.getDatas = function() {
        var full = [];
        for(data in this.datas) {
            var datas = [];
            for(field in this.axes) {
                avg = this.datas[data][field];
                max = this.axes[field].max;
                if (this.axes[field].hasOwnProperty('divided')) {
                    if (avg && avg > 0) { datas.push( avg*100/this.datas[data][this.axes[field].divided]); } else { datas.push(0); }
                }else {
                    if (avg && avg > 0) { datas.push(avg*100/max); } else { datas.push(0); }
                }
            }
            full.push(datas);
        }
        return full;
    }

    this.template = function(config, datas, template) {
        config = config === undefined ? false : config;
        datas = datas === undefined ? false : datas;
        template = template === undefined ? false : template;
    }

    this.doend = function(config) {
        datas = this.getDatas();
        if (this.usetables) {
            this.tables();
        }
        var id = this.hasOwnProperty('connect') ? this.connect : config;
        id = "render-" + id;
        if (!this.radartodraw) { 
            this.radartodraw = new RGraph.SVG.Radar({
                id: id,
                data: datas,
                options: {
                    labels: this.getLabels(config),
                    colors: this.colors,
                    linewidth: 2,
                    scaleVisible: false,
                    scaleMax: 100,
                    filled: true,
                    filledAccumulative: false,
                    backgroundGridColor: 'gray',
                    tickmarksStyle: 'filledcircle',
                    tickmarksSize: 0,
                    labelsAbove: true,
                }
            }).responsive(this.responsive);
        } else{
            RGraph.SVG.clear(this.radartodraw.svg);
        }
        if (this.addresults) {
            this.radartodraw.set("labels", this.getLabels(config, true));
        }
        this.radartodraw.originalData = datas;
        this.radartodraw.draw();
    }

    this.tables = function() {
        for (data in this.datas) {
            var id = this.hasOwnProperty('connect') ? this.connect : data;
            var table = document.getElementById("table-" + id + "-" + data);
            table.innerHTML = "";

            var datas = [];
            for(field in this.axes) {
                avg = this.datas[data][field];
                max = this.axes[field].max;
                percent = this.axes[field].hasOwnProperty('percent') ? true : false;
                if (avg && avg > 0) {
                    var value = percent ? Math.round(avg*100/max).toLocaleString('en') : avg.toFixed(this.axes[field].fixed).toLocaleString('en');
                    var mesure = value > 1 ? this.axes[field].pmesure : this.axes[field].mesure;
                    var name = value > 1 ? this.axes[field].pname : this.axes[field].name;
                } else {
                    var value = 0;
                    var mesure = this.axes[field].mesure;
                    var name = this.axes[field].name;
                }
                var tr = document.createElement("tr");
                var td_data = document.createElement("td");
                var td_name = document.createElement("td");
                num = Number(value).toLocaleString();
                td_data.innerHTML = num + mesure;
                td_name.innerHTML = name;
                tr.appendChild(td_data);
                tr.appendChild(td_name);
                table.appendChild(tr);
            }
        }
    }
}