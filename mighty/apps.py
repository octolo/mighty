from django.conf import settings
from django.apps import AppConfig
from mighty import exclude
from mighty import over_config
import os, logging

class Config:
    site = None
    site_header = "Back office"
    index_title = "Home"
    paginate_by = 100
    exclude_content_type = {"id__gt": 9}
    exclude = exclude
    supervision = True
    user_or_invitation = 'auth.UserOrInvitation'
    jwt_enable = False
    
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

    class Interpreter:
        _idorarg = 'IDorARG'
        _filter = ['f', '(', ')']
        _family = ['(', ')']
        _or = '~'
        _split= ','
        _split_values = ' '

    class Crypto:
        BS = 16

if hasattr(settings, 'MIGHTY'): over_config(Config, getattr(settings, 'MIGHTY'))
class MightyConfig(AppConfig, Config):
    name = "mighty"