from django.apps import AppConfig
from django.conf import settings


class Config:
    groups_onsave = []
    mail_protect_spam = 5
    sms_protect_spam = 5
    minutes_allowed = 5
    code_size = 6
    email_code = 'twofactor/email_code.html'
    email_template = None
    accounts_market = []
    template_id = None

    class method:
        email = True
        sms = True
        basic = False

    class regex:
        phone = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'


# Use new MISSIVE_* settings instead of deprecated TWOFACTOR
if hasattr(settings, 'MISSIVE_GROUPS_ONSAVE'):
    Config.groups_onsave = settings.MISSIVE_GROUPS_ONSAVE
if hasattr(settings, 'MISSIVE_MAIL_PROTECT_SPAM'):
    Config.mail_protect_spam = settings.MISSIVE_MAIL_PROTECT_SPAM
if hasattr(settings, 'MISSIVE_SMS_PROTECT_SPAM'):
    Config.sms_protect_spam = settings.MISSIVE_SMS_PROTECT_SPAM
if hasattr(settings, 'MISSIVE_MINUTES_ALLOWED'):
    Config.minutes_allowed = settings.MISSIVE_MINUTES_ALLOWED
if hasattr(settings, 'MISSIVE_EMAIL_CODE_TEMPLATE'):
    Config.email_code = settings.MISSIVE_EMAIL_CODE_TEMPLATE
if hasattr(settings, 'MISSIVE_EMAIL_TEMPLATE'):
    Config.email_template = settings.MISSIVE_EMAIL_TEMPLATE
if hasattr(settings, 'MISSIVE_ACCOUNTS_MARKET'):
    Config.accounts_market = settings.MISSIVE_ACCOUNTS_MARKET
if hasattr(settings, 'MISSIVE_OTP_TEMPLATE_ID'):
    Config.template_id = settings.MISSIVE_OTP_TEMPLATE_ID


class TwofactorConfig(AppConfig, Config):
    name = 'mighty.applications.twofactor'
