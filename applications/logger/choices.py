from mighty.applications.logger.apps import LoggerConfig as conf

EMERG = conf.Code.emerg
ALERT = conf.Code.alert
CRITICAL = conf.Code.critical
ERROR = conf.Code.error
WARNING = conf.Code.warning
NOTICE = conf.Code.notice
INFO = conf.Code.info
DEBUG = conf.Code.debug
LEVEL = (
    (EMERG, 'EMERGENCY'),
    (ALERT, 'ALERT'),
    (CRITICAL, 'CRITICAL'),
    (ERROR, 'ERROR'),
    (WARNING, 'WARNING'),
    (NOTICE, 'NOTICE'),
    (INFO, 'INFO'),
    (DEBUG, 'DEBUG'),
)
