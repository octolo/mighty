from django.db import models
from mighty.applications.logger.apps import LoggerConfig as conf
from django.contrib.auth import get_user_model
UserModel = get_user_model()

EMERG = conf.Code.emerg
ALERT = conf.Code.alert
CRITICAL = conf.Code.critical
ERROR = conf.Code.error
WARNING = conf.Code.warning
NOTICE = conf.Code.notice
INFO = conf.Code.info
DEBUG = conf.Code.debug
LEVEL_CHOICES = (
    (EMERG, "EMERGENCY"),
    (ALERT, "ALERT"),
    (CRITICAL, "CRITICAL"),
    (ERROR, "ERROR"),
    (WARNING, "WARNING"),
    (NOTICE, "NOTICE"),
    (INFO, "INFO"),
    (DEBUG, "DEBUG"),
)
class Log(models.Model):
    date = models.DateTimeField(auto_now_add=True, editable=False)
    code = models.SmallPositiveIntegerField(choices=LEVEL_CHOICES, default=DEBUG, editable=False)
    message = models.TextField(editable=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, blank=True, editable=False, null=True)

