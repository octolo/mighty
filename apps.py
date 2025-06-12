import os

from django.apps import AppConfig
from django.conf import settings

from . import exclude, over_config


class Config:
    use_rest = False
    rest_error = 'rest_framework.serializers.ValidationError'
    cgu_path = '/static/files/CGU.pdf'
    politic_path = '/static/files/POLITIQUE_DE_CONFIDENTIALITE_JANV_2024.pdf'
    enable_mimetype = False
    named_tpl = '%(named)s-%(id)s'
    logo = '/static/img/logo.png'
    domain = 'localhost:8000'
    webhook = 'localhost:8000'
    site_header = 'Back office'
    index_title = 'Home'
    paginate_by = 100
    exclude_content_type = {'id__gt': 9}
    exclude = exclude
    enable_supervision = False
    enable_channel = False
    jwt_enable = False
    days_in_year = 365.25
    backend_task = 'mighty.backends'
    consumers = {'chat': 'mighty.applications.messenger.consumers.ChatConsumer'}
    auth_consumer = 'channels.auth.AuthMiddlewareStack'
    config_simple = {'current_maintenance': False}
    reporting_content_type = (
        ('csv', '.csv'),
        ('xls', '.xls'),
        ('xlsx', '.xlsx'),
    )
    most_used_app = ()
    multi_apps = {
        'messenger': [
            'Missive',
            'Notification',
            'Template',
        ],
        'languages/translations': [
            'Nationality',
            'Translator',
        ],
        'user': [
            'User',
            'Twofactor',
            'Trashmail',
            'MergeableAccount',
        ],
        'Logger': [
            'Log',
            'ModelChangeLog',
        ],
        'Configuration': [
            'Backend',
            'Reporting',
            'ConfigSimple',
            'ConfigClient',
            'TemplateVariable',
            'MimeType',
        ],
        'Websocket': [
            'Channel',
        ],
    }
    pdf_options = {
        'quiet': '',
        'disable-smart-shrinking': '',
        'no-outline': '',
        'lowquality': '',
        'javascript-delay': '0',
        'encoding': 'UTF-8',
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'custom-header': [('Accept-Encoding', 'gzip')],
    }
    urls_admin_to_add = []
    pdf_header = 'document_header_template.html'
    pdf_footer = 'document_footer_template.html'
    pdf_content = 'document_content_template.html'

    class Directory:
        app = os.path.dirname(os.path.realpath(__file__))
        certificates = f'{settings.BASE_DIR}/certs'
        cache = f'{settings.BASE_DIR}/cache'
        logs = f'{settings.BASE_DIR}/logs'
        cloud = 'cloud/'
        process = 'process/'

    class Test:
        search = [
            'none',
            '',
            0,
            'na',
            'n/a',
            '-',
            '/',
            '\\',
            '?',
            '??',
            '#n/a',
            '#value!',
            'nc',
            'n/c',
            'ns',
        ]
        replace = ['_', ';', ',']
        intflt_toreplace = [' ', ',', '€', '$', '%']
        intnotint = [
            'IntegerField',
            'FloatField',
            'DecimalField',
            'SmallIntegerField',
            'PositiveIntegerField',
            'PositiveSmallIntegerField',
        ]
        forbidden = ['id', 'display']
        retrieve = ['id']
        mandatory = []
        associates = []
        unique = []
        uncomment = []
        keepcomment = []

    class Service:
        services = ['server']
        uptime = (
            "ps -u %s -o etimes,cmd | awk '{print $1}' | tail -n1  | tr -d '\n'"
        )
        cpu = 'ps -u %s -o %%cpu --no-headers'
        memory = 'ps -u %s -o %%mem --no-headers'

    class Channel:
        delimiter = '__'

    class FileSystem:
        unix = ['permissions', 'owner', 'group', 'size', 'modified', 'name']
        line_template = '%(space)s%(label)s: %(data)s'
        unit = '%s %s'
        units_mapping = {
            'PB': [1 << 50, 'petabytes', 'petabyte'],
            'TB': [1 << 40, 'terabytes', 'terabyte'],
            'GB': [1 << 30, 'gigabytes', 'gigabyte'],
            'MB': [1 << 20, 'megabytes', 'megabyte'],
            'KB': [1 << 10, 'kilobytes', 'kilobyte'],
            'B': [1 << 0, 'bytes', 'byte'],
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


if hasattr(settings, 'MIGHTY'):
    over_config(Config, settings.MIGHTY)


class MightyConfig(AppConfig, Config):
    name = 'mighty'
