from mighty.applications.logger.apps import LoggerConfig as conf
from mighty.applications.logger.backends import LoggerBackend
import logging

logging.basicConfig(format='%(message)s')
logger = logging.getLogger(__name__)
class LoggerBackend(LoggerBackend):
    def level(self, lvl):
        logger.setLevel(10)
        super().level(lvl)

    def send(self, lvl, log):
        logger.log(getattr(conf.Code, lvl), log)
