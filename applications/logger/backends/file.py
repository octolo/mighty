from django.conf import settings
from mighty.applications.logger.apps import LoggerConfig as conf
from mighty.apps import MightyConfig
from mighty.applications.logger.backends import LoggerBackend

class LoggerBackend(LoggerBackend):
    def send(self, lvl, log):
        logfile = '%s/%s' % (MightyConfig.Directory.logs, f"{datetime.datetime.now():%Y%m%d}")
        log = open(logfile, conf.Log.file_open_method)
        log.write(log)
        log.close()