from mighty.applications.logger.apps import LoggerConfig as conf
from mighty.applications.logger.backends import LoggerBackend

class LoggerBackend(LoggerBackend):
    def send(self, lvl, log):
        print("%s%s%s" % (getattr(conf.Color, lvl), log, conf.Color.default))