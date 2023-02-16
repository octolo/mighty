"""
Log what you want in your configured system.
You can configure the MIGHTY config array Log:
-- Log
    - log_level
    - log_type (systlog, file, console)
[app] Your app name where the log from
[lvl] Level log
0 	Emergency 	  emerg (panic)	 Système inutilisable.
1 	Alert 	      alert          Une intervention immédiate est nécessaire.
2 	Critical 	  crit 	         Erreur critique pour le système.
3 	Error 	      err (error) 	 Erreur de fonctionnement.
4 	Warning 	  warn (warning) Avertissement (une erreur peut intervenir si aucune action n"est prise).
5 	Notice 	      notice  	     Evénement normal méritant d"être signalé.
6 	Informational info 	         Pour information.
7 	Debugging 	  debug 	     Message de mise au point.
[msg] Message about the log
[user] If is not none add the user in the log
"""
from django.conf import settings
from mighty.applications.logger.apps import LoggerConfig as conf
from mighty.applications.logger import fields
import datetime, logging, sys

LOG_LEVEL_IN_DB = getattr(settings, 'LOG_LEVEL_IN_DB', 100)
LOG_IN_DB = getattr(settings, 'LOG_IN_DB', False)
def log_in_db(record, msg, only_except=False):
    if only_except:
        if record.exc_text: pass
        else: return

    if 'mighty.applications.logger' in settings.INSTALLED_APPS and LOG_LEVEL_IN_DB >= record.levelno:
        from mighty.models import Log
        dblog = Log(msg=str(record.exc_info[1]), stack_info=record.exc_text)
        for field in fields.log:
            if field not in ['id', 'created', 'content_type', 'object_id', 'content_object', 'log_hash', 'stack_info', 'msg']:
                setattr(dblog, field, str(getattr(record, field)))
        if hasattr(record, "log_in_db"):
            lib = record.log_in_db
            if hasattr(lib, 'app_label') and hasattr(lib, 'model_name'):
                from django.contrib.contenttypes.models import ContentType
                dblog.content_type = ContentType.objects.get(app_label=record.log_in_db.app_label, model=record.log_in_db.model_name.lower())
                dblog.object_id = record.log_in_db.id
        try:
            dblog.save()
        except Exception as e:
            pass
        logmodel = Log.objects.get(log_hash=dblog.get_log_hash())
        return logmodel

class NotifySlackDiscord:
    def slack_notify(self, record, dblog=None):
        if getattr(settings, "SLACK_NOTIFY", False):
            from mighty.applications.logger.notify.slack import SlackLogger
            slack = SlackLogger(record=record, dblog=dblog)
            slack.send_error()

    def discord_notify(self, record, dblog=None):
        if getattr(settings, "DISCORD_NOTIFY", False):
            from mighty.applications.logger.notify.discord import DiscordLogger
            discord = DiscordLogger(record=record, dblog=dblog)
            discord.send_error()

class ConsoleHandler(logging.StreamHandler, NotifySlackDiscord):
    dblog = None
    def format(self, record):
        msg = super().format(record)
        msg = conf.Log.format_user.format(record.user.logname, msg) if hasattr(record, 'user') and hasattr(record.user, 'logname') else msg
        if getattr(record, 'log_in_db', False):
            self.dblog = log_in_db(record, msg)
        elif LOG_IN_DB:
            self.dblog = log_in_db(record, msg, True)
        msg = "%s%s%s" % (getattr(conf.Color, record.levelname.lower()), msg, conf.Color.default)
        if sys.exc_info()[1].__class__.__name__ not in conf.Log.without_notify:
            self.slack_notify(record=record, dblog=self.dblog)
            self.discord_notify(record=record, dblog=self.dblog)
        return msg

    def emit(self, record):
        super().emit(record)

class FileHandler(logging.FileHandler, NotifySlackDiscord):
    dblog = None
    def format(self, record):
        msg = super().format(record)
        msg = conf.Log.format_user.format(record.user.logname, msg) if hasattr(record, 'user') and hasattr(record.user, 'logname') else msg
        if getattr(record, 'log_in_db', False):
            self.dblog = log_in_db(record, msg)
        elif LOG_IN_DB:
            self.dblog = log_in_db(record, msg, True)
        msg = "%s%s%s" % (getattr(conf.Color, record.levelname.lower()), msg, conf.Color.default)
        self.slack_notify(record=record, dblog=self.dblog)
        self.discord_notify(record=record, dblog=self.dblog)
        return msg

    def emit(self, record):

        super().emit(record)

class DatabaseHander(logging.StreamHandler):
    pass