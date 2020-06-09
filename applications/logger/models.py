from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth import get_user_model
from mighty.applications.logger.apps import LoggerConfig as conf
from mighty.applications.logger import translates as _

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
    args = models.CharField(_.args, max_length=255, blank=True, null=True)
    created = models.DateTimeField(_.created, auto_now_add=True, editable=False)
    exc_info = models.CharField(_.exc_info, max_length=255, blank=True, null=True)
    filename = models.CharField(_.filename, max_length=255, blank=True, null=True)
    funcName = models.CharField(_.funcName, max_length=255, blank=True, null=True)
    levelno = models.PositiveSmallIntegerField(_.levelno, blank=True, null=True)
    lineno = models.CharField(_.lineno, max_length=255, blank=True, null=True)
    module = models.CharField(_.module, max_length=255, blank=True, null=True)
    msecs = models.CharField(_.msecs, max_length=255, blank=True, null=True)
    msg = models.CharField(_.msg, max_length=255, blank=True, null=True)
    name = models.CharField(_.name, max_length=255, blank=True, null=True)
    pathname = models.CharField(_.pathname, max_length=255, blank=True, null=True)
    process = models.CharField(_.process, max_length=255, blank=True, null=True)
    processName = models.CharField(_.processName, max_length=255, blank=True, null=True)
    relativeCreated = models.CharField(_.relativeCreated, max_length=255, blank=True, null=True)
    stack_info = models.TextField(_.stack_info, max_length=255, blank=True, null=True)
    thread = models.CharField(_.thread, max_length=255, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True

class ChangeLog(models.Model):
    model_id = models.ForeignKey('', on_delete=models.CASCADE)
    field = models.CharField(_.field, max_length=255, db_index=True)
    value = models.BinaryField(_.value, )
    fmodel = models.CharField(_.fmodel, max_length=255)
    date_begin = models.DateTimeField(_.date_begin, editable=False)
    date_end = models.DateTimeField(_.date_end, auto_now_add=True, editable=False)
    user = models.CharField(max_length=255)

    def get_value(self):
        return self.value.decode('utf-8')

    class Meta:
        abstract = True
        verbose_name = _.v_log
        verbose_name_plural = _.vp_log
        ordering = ['-date_end']