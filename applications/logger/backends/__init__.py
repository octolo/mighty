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
import datetime

#DB_ACTIVE = False
#if 'mighty.applications.logger' in settings.INSTALLED_APPS:
#    from mighty.models import Log
#    DB_ACTIVE = True

class LoggerBackend:
    def __init__(self):
        self.lvl_auth = conf.Log.log_level
        self.log_type = conf.Log.log_type

    def log(self, lvl, msg, user=None, *args, **kwargs):
        lvl_auth = kwargs["loglvlauth"] if "loglvlauth" in kwargs else self.lvl_auth
        lvl_auth = getattr(conf.Code, lvl_auth)
        log_type = kwargs["logtype"] if "logtype" in kwargs else self.log_type
        app = kwargs["app"] if "app" in kwargs else None
        log_lvl = getattr(conf.Code, lvl)
        log_in_db = kwargs["logindb"] if "logindb" in kwargs and DB_ACTIVE else False
        if log_lvl >= lvl_auth:
            if user is not None: msg = conf.Log.format_user.format(user.username, user.id, msg)
            if app is not None: msg = "[%s] %s" % (app, msg)
            log = conf.Log.format_log.format(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S.%f}", lvl, msg)
            self.send(lvl, log)
            if log_in_db:
                self.send_db(log_lvl, log, user)
    
    def level(self, lvl):
        self.lvl_auth = lvl

    def debug(self, msg, user=None, *args, **kwargs):
        self.log('debug', msg, user, *args, **kwargs)

    def info(self, msg, user=None, *args, **kwargs):
        self.log('info', msg, user, *args, **kwargs)
        
    def warning(self, msg, user=None, *args, **kwargs):
        self.log('warning', msg, user, *args, **kwargs)

    def critical(self, msg, user=None, *args, **kwargs):
        self.log('critical', msg, user, *args, **kwargs)

    def send(self, lvl, log):
        pass

    def send_db(self, lvl, log, user=None):
        pass
        #dblog = Log(code=lvl, message=log, user=User)
        #dblog.save()