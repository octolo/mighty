from django.db import models
from django.contrib.auth import get_user_model
from mighty.applications.logger.apps import LoggerConfig as conf
from mighty.applications.logger import translates as _
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
    (DEBUG, "DEBUG"))
class Log(models.Model):
    date = models.DateTimeField(auto_now_add=True, editable=False)
    code = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=DEBUG, editable=False)
    message = models.TextField(editable=False)
    user = models.CharField(max_length=255)

class LogModel(models.Model):
    model_id = models.ForeignKey('', on_delete=models.CASCADE)
    field = models.CharField(_.field, max_length=255, db_index=True)
    value = models.BinaryField(_.value, )
    fmodel = models.CharField(_.fmodel, max_length=255)
    date_begin = models.DateTimeField(_.date_begin, )
    date_end = models.DateTimeField(_.date_end, auto_now_add=True, editable=False)
    user = models.CharField(max_length=255)

    def get_value(self):
        return self.value.decode('utf-8')

    class Meta:
        abstract = True
        verbose_name = _.v_log
        verbose_name_plural = _.vp_log
        ordering = ['-date_end']