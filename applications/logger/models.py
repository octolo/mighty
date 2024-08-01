from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth import get_user_model
from mighty.models.base import Base
from mighty.applications.logger import translates as _, choices
from mighty import translates as _m
from datetime import datetime
import hashlib

class Log(Base):
    fields_log_hash = ("msg", "stack_info")
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
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    log_hash = models.CharField(max_length=40, unique=True, blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = _.v_log
        verbose_name_plural = _.vp_log
        ordering = ['-created']

    def get_log_hash(self):
        fields_to_hash = "".join(getattr(self, field) for field in self.fields_log_hash)
        return hashlib.sha1(fields_to_hash.encode()).hexdigest()

    def save(self, *args, **kwargs):
        self.log_hash = self.get_log_hash()
        super().save(*args, **kwargs)

class ChangeLog(models.Model):
    field = models.CharField(_m.field, max_length=255, db_index=True)
    value = models.BinaryField(_m.value)
    fmodel = models.CharField(_m.fmodel, max_length=255)
    date_begin = models.DateTimeField(_m.date_begin, editable=False)
    date_end = models.DateTimeField(_m.date_end, editable=False, auto_now_add=True)
    user = models.CharField(max_length=255, blank=True, null=True, default='anonymous~root')

    def get_value(self):
        if hasattr(self.value, 'decode'):
            return self.value.decode('utf-8')
        elif hasattr(self.value, 'tobytes'):
            return self.value.tobytes().decode('utf-8')
        return "Can't cast/bytes/decode"

    class Meta:
        abstract = True
        verbose_name = _.v_changelog
        verbose_name_plural = _.vp_changelog
        ordering = ['-date_end']

class ModelChangeLog(ChangeLog):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta(ChangeLog.Meta):
        abstract = True

class AccessLog(models.Model):
    object_id = models.ForeignKey('', on_delete=models.CASCADE)
    date_access = models.DateTimeField(_.date_access, editable=False)
    user = models.CharField(max_length=255, default='anonymous~root')

    class Meta:
        abstract = True
        verbose_name = _.v_accesslog
        verbose_name_plural = _.vp_accesslog
        ordering = ['-date_access']
