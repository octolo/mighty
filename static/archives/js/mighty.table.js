function Mtable(url, options) {
    Mcommon.call(this, url, options);

    this.original_after = this.after;
    this.after = function(config, response, action, datas) {
        this.original_after(config, response, action, datas);
    }

    this.original_events = this.events;
    this.events = function() {
        this.original_events();
    }
    
    
    this.hideable = function(hide, title) {
        if (hide && title) {
            for (config in this.config) {
                document.getElementById(this.actions.hide + config).style.display = "none";
            }
        }
    }

    this.hider = function(config) {
        //alert(config);
        //for (config in this.config) {
        //    document.getElementById(this.actions.hide + show).style.display = "none";
        //}
        //document.getElementById(this.actions.hide + show).style.display = "block";
    }

}