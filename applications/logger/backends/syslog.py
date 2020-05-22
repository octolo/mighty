from mighty.applications.logger.apps import LoggerConfig as conf
from mighty.applications.logger.backends import LoggerBackend
import syslog

class LoggerBackend(LoggerBackend):
    emerg = 0
    alert = 1
    crit = 2
    error = 3
    warning = 4
    notice = 5
    info = 6
    debug = 7

    def send(self, lvl, log):
        syslog.openlog(logoption=syslog.LOG_PID)
        syslog.syslog(getattr(self, lvl), msg)
        syslog.closelog()