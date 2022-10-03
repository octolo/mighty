from django.conf import settings
from django.apps import AppConfig
from . import exclude
from . import over_config
import os, logging

class Config:
    enable_mimetype = False
    named_tpl = "%(named)s-%(id)s"
    logo = "/static/img/logo.png"
    domain = "localhost:8000"
    webhook = "localhost:8000"
    site_header = "Back office"
    index_title = "Home"
    paginate_by = 100
    exclude_content_type = {"id__gt": 9}
    exclude = exclude
    supervision = True
    user_or_invitation = 'auth.UserOrInvitation'
    jwt_enable = False
    days_in_year = 365.25
    backend_task = 'mighty.backends'
    consumers = {'chat': 'mighty.applications.messenger.consumers.ChatConsumer'}
    auth_consumer = 'channels.auth.AuthMiddlewareStack'
    config_simple = {
        'current_maintenance': False,
    }
    multi_apps = {
        'messenger': [
            'Missive',
            'Notification',
            'Invitation',
        ],
        'languages/translations': [
            'Nationality',
            'Translator',
        ],
        'shop': [
            'Service',
            'Offer',
            'Subscription',
            'Discount',
            'Bill',
            'PaymentMethod',
            'SubscriptionRequest',
        ],
        'user': [
            'User',
            'Twofactor',
            'Trashmail'
        ],
        'dataprotect': [
            'ServiceData',
            'UserDataProtect',
        ],
        'Configuration': [
            'ConfigSimple',
            'ConfigClient',
        ],
        'Websocket': [
            'Channel',
        ]
    }
    pdf_options = {
            'encoding': 'UTF-8',
            'page-size':'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'custom-header' : [
                ('Accept-Encoding', 'gzip')
            ]
        }
    pdf_header = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <style type="text/css">
    body { padding-bottom: 5px; }
    </style>
    <script>
    function subst() {
        var vars = {};
        var query_strings_from_url = document.location.search.substring(1).split('&');
        for (var query_string in query_strings_from_url) {
            if (query_strings_from_url.hasOwnProperty(query_string)) {
                var temp_var = query_strings_from_url[query_string].split('=', 2);
                vars[temp_var[0]] = decodeURI(temp_var[1]);
            }
        }
        var css_selector_classes = ['page', 'frompage', 'topage', 'webpage', 'section', 'subsection', 'date', 'isodate', 'time', 'title', 'doctitle', 'sitepage', 'sitepages'];
        for (var css_class in css_selector_classes) {
            if (css_selector_classes.hasOwnProperty(css_class)) {
                var element = document.getElementsByClassName(css_selector_classes[css_class]);
                for (var j = 0; j < element.length; ++j) {
                    element[j].textContent = vars[css_selector_classes[css_class]];
                }
            }
        }
    }
    </script>
  </head>
  <body onload="subst()">%s</body>
</html>"""
    pdf_footer = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <style type="text/css">
    body { margin-top: 5px; }
    </style>
    <script>
    function subst() {
        var vars = {};
        var query_strings_from_url = document.location.search.substring(1).split('&');
        for (var query_string in query_strings_from_url) {
            if (query_strings_from_url.hasOwnProperty(query_string)) {
                var temp_var = query_strings_from_url[query_string].split('=', 2);
                vars[temp_var[0]] = decodeURI(temp_var[1]);
            }
        }
        var css_selector_classes = ['page', 'frompage', 'topage', 'webpage', 'section', 'subsection', 'date', 'isodate', 'time', 'title', 'doctitle', 'sitepage', 'sitepages'];
        for (var css_class in css_selector_classes) {
            if (css_selector_classes.hasOwnProperty(css_class)) {
                var element = document.getElementsByClassName(css_selector_classes[css_class]);
                for (var j = 0; j < element.length; ++j) {
                    element[j].textContent = vars[css_selector_classes[css_class]];
                }
            }
        }
    }
    </script>
  </head>
  <body onload="subst()">%s</body>
</html>"""
    pdf_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset=UTF-8" />
</head>
<body><br><br>%s</body>
</html>"""

    class Directory:
        app          = os.path.dirname(os.path.realpath(__file__))
        certificates = "%s/certs" % settings.BASE_DIR
        cache        = "%s/cache" % settings.BASE_DIR
        logs         = "%s/logs" % settings.BASE_DIR
        cloud        = 'cloud/'
        process      = 'process/'

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

    class Service:
        services = ['server',]
        uptime = "ps -u %s -o etimes,cmd | awk '{print $1}' | tail -n1  | tr -d '\n'"
        cpu = 'ps -u %s -o %%cpu --no-headers'
        memory = 'ps -u %s -o %%mem --no-headers'

    class Channel:
        delimiter = '__'

    class FileSystem:
        unix = ["permissions", "owner", "group", "size", "modified", "name"]
        line_template = '%(space)s%(label)s: %(data)s'
        unit = '%s %s'
        units_mapping = {
            'PB': [1<<50, 'petabytes', 'petabyte'],
            'TB': [1<<40, 'terabytes', 'terabyte'],
            'GB': [1<<30, 'gigabytes', 'gigabyte'],
            'MB': [1<<20, 'megabytes', 'megabyte'],
            'KB': [1<<10, 'kilobytes', 'kilobyte'],
            'B':  [1<<0,  'bytes',     'byte'],
        }

    class Interpreter:
        _idorarg = 'IDorARG'
        _filter = ['f', '(', ')']
        _family = ['(', ')']
        _or = '~'
        _split = ','
        _negative = '-'

    class Crypto:
        BS = 16

if hasattr(settings, 'MIGHTY'): over_config(Config, getattr(settings, 'MIGHTY'))
class MightyConfig(AppConfig, Config):
    name = "mighty"
