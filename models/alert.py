"""
Model class
Add alerts field at the model

(get_alert) return the alert field by lvl param
(add_alert) add an alert to a field by lvl param
(is_in_alert) return bool if model have an alert
(alert_html) return the html alert
(info_html) return the info lvl html
(error_html) return the error lvl html
(alerts_html) return all alerts in html
(infos_html) return all infos lvl in html
(errors_html) return all errors lvl in html
(is_in_info) return bool if model have an info
(is_in_error) return bool if model have an error
"""
from django.db import models
from mighty.models import JSONField
from django.utils.html import format_html

def default_alert_dict():
    return {"infos": {}, "errors": {}}

class Alert(models.Model):
    alerts = JSONField(blank=True, null=True, default=default_alert_dict)

    class Meta:
        abstract = True

    def get_alert(self, lvl, field):
        return self.alerts[lvl][field]

    def add_alert(self, lvl, field, msg):
        self.alerts[lvl][field] = msg

    def is_in_alert(self, lvl):
        return True if len(self.alerts[lvl]) else False

    def alert_html(self, lvl, field):
        alert = [ '<div class="%s">' % lvl[:-1],
            """<span class="closebtn-alert" onclick="this.parentElement.style.display='none';">""",
            '&times;</span>%s</div>' % self.alerts[lvl][field],]        
        return  format_html("".join(alert))

    def info_html(self, field):
        return self.alert_html("infos", field)

    def error_html(self, field):
        return self.alert_html("errors", field)

    def alerts_html(self, lvl):
        return "".join([getattr("%s_html" % lvl, field) for field in self.alerts[lvl]])

    @property
    def infos_html(self): return alerts_html("infos")
    @property
    def errors_html(self): return alerts_html("errors")
    @property
    def is_in_info(self): return self.is_in_alert("info")
    @property
    def is_in_error(self): return self.is_in_alert("error")