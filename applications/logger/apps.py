from django.apps import AppConfig
from django.conf import settings
import logging

class Config:
    class Log:
        logger = "logger_{}"
        log_type = "default"
        log_level = "info"
        format_log = "{} - {} | {}"
        format_user = "{}.{} - {}"
        format_code = "{}_code"
        format_color = "{}_color"
        file_open_method = "a"
        name_file = "{}/{}_{}_{}_{}.log"

    class Color:
        default = "\033[0m"
        emerg = "\033[1;93;5;101m"
        alert = "\033[1;30;5;105m"
        crit = "\033[1;97;5;101m"
        error = "\033[1;91;5;107m"
        warning = "\033[0;91m"
        notice = "\033[0;97m"
        info = "\033[0;94m"
        debug = "\033[0;30;100m"

    class Code:
        emerg = 60
        alert = 55
        critical = 50
        error = 40
        warning = 30
        notice = 25
        info = 20
        debug = 10

if hasattr(settings, 'LOGGER'):
    for config,configs in getattr(settings, 'LOGGER').items():
        if hasattr(Config, config):
            for key,value in configs.items():
                if hasattr(getattr(Config, config), key):
                    setattr(getattr(Config, config), key, value)

class LoggerConfig(AppConfig, Config):
    name = 'mighty.applications.logger'
