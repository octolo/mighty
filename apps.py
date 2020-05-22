from django.apps import AppConfig
from django.conf import settings
from mighty import exclude
import os, logging

class Config:
    site_header = "Back office"
    index_title = "Home"
    paginate_by = 100
    exclude_content_type = {"id__gt": 9}
    exclude = exclude
    
    class Directory:
        app          = os.path.dirname(os.path.realpath(__file__))
        certificates = "%s/certs" % settings.BASE_DIR
        cache        = "%s/cache" % settings.BASE_DIR
        logs         = "%s/logs" % settings.BASE_DIR

    class Test:
        search = ["none", "", 0, "na", "n/a", "-", "/", "\\", "?", "??", "#n/a", "#value!", "nc", "n/c", "ns",]
        replace = ["_", ";", ","]
        intflt_toreplace = [" ", ",", "€", "$", "%"]
        intnotint = ["IntegerField", "FloatField", "DecimalField", "SmallIntegerField", "PositiveIntegerField", "PositiveSmallIntegerField"]
        forbidden = ["id", "display"]
        retrieve = ["id",]
        mandatory = []
        associates = []
        unique = []
        uncomment = []
        keepcomment = []

    class Crypto:
        BS = 16

    class Log:
        logger = "logger_{}"
        log_type = "default"
        log_level = 7
        format_log = "{} - {} | {}"
        format_user = "{}.{} - {}"
        format_code = "{}_code"
        format_color = "{}_color"
        file_open_method = "a"
        name_file = "{}/{}_{}_{}_{}.log"
        default_color = "\033[0m"
        emerg_code = 60
        emerg_color = "\033[1;93;5;101m"
        alert_code = 55
        alert_color = "\033[1;30;5;105m"
        crit_code = logging.CRITICAL #50
        crit_color = "\033[1;97;5;101m"
        error_code = logging.ERROR #40
        error_color = "\033[1;91;5;107m"
        warning_code = logging.WARNING #30
        warning_color = "\033[0;91m"
        notice_code = 25
        notice_color = "\033[0;97m"
        info_code = logging.INFO #20
        info_color = "\033[0;94m"
        debug_code = logging.DEBUG #10
        debug_color = "\033[0;30;100m"

"""
Override settings from the settings.py
MIGHTY = {"site_header": "my new site header", "Log": {"log_type": "syslog"}}
"""
if hasattr(settings, "MIGHTY"):
    for config,configs in getattr(settings, "MIGHTY").items():
        if hasattr(Config, config):
            for key,value in configs.items():
                if hasattr(getattr(Config, config), key):
                    setattr(getattr(Config, config), key, value)

class MightyConfig(AppConfig, Config):
    name = "mighty"