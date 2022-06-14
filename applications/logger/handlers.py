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
import datetime, logging

LOG_LEVEL_IN_DB = getattr(settings, 'LOG_LEVEL_IN_DB', 100)
def log_in_db(record, msg):
    if 'mighty.applications.logger' in settings.INSTALLED_APPS and LOG_LEVEL_IN_DB >= record.levelno and \
        hasattr(record.log_in_db, 'app_label') and hasattr(record.log_in_db, 'model_name'):
        from django.contrib.contenttypes.models import ContentType
        from mighty.models import Log
        dblog = Log()
        for field in Log._meta.fields:
            if field.name not in ['id', 'created', 'content_type', 'object_id', 'content_object']:
                setattr(dblog, field.name, str(getattr(record, field.name)))
        dblog.content_type = ContentType.objects.get(app_label=record.log_in_db.app_label, model=record.log_in_db.model_name.lower())
        dblog.object_id = record.log_in_db.id
        dblog.save()

class NotifySlackDiscord:
    def slack_notify(self, record):
        from mighty.applications.logger.notify.slack import SlackLogger
        slack = SlackLogger(record=record)
        slack.send_error()

    def discord_notify(self, record):
        from mighty.applications.logger.notify.discord import DiscordLogger
        discord = DiscordLogger(record=record)
        discord.send_error()

class ConsoleHandler(logging.StreamHandler, NotifySlackDiscord):
    def format(self, record):
        msg = super().format(record)
        if hasattr(record, 'user'):
            msg = conf.Log.format_user.format(record.user.logname, msg) if hasattr(record, 'user') and hasattr(record.user, 'logname') else msg
        if getattr(record, 'log_in_db', False):
            log_in_db(record, msg)
        msg = "%s%s%s" % (getattr(conf.Color, record.levelname.lower()), msg, conf.Color.default)
        return msg

    def emit(self, record):
        self.slack_notify(record=record)
        self.discord_notify(record=record)
        super().emit(record)

class FileHandler(logging.FileHandler, NotifySlackDiscord):
    def format(self, record):
        msg = super().format(record)
        msg = conf.Log.format_user.format(record.user.logname, msg) if hasattr(record, 'user') and hasattr(record.user, 'logname') else msg
        if getattr(record, 'log_in_db', False):
            log_in_db(record, msg)
        return msg

    def emit(self, record):
        self.slack_notify(record=record)
        self.discord_notify(record=record)
        super().emit(record)

class DatabaseHander(logging.StreamHandler):
    pass