from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from mighty.applications.extend import translates as _
from mighty.models.base import Base

BIGINTEGER = 'BIGINTEGER'
BINARY = 'BINARY'
BOOLEAN = 'BOOLEAN'
CHAR = 'CHAR'
DATE = 'DATE'
DECIMAL = 'DECIMAL'
DURATION = 'DURATION'
EMAIL = 'EMAIL'
FILE = 'FILE'
FLOAT = 'FLOAT'
IMAGE = 'IMAGE'
INTEGER = 'INTEGER'
SMALLINTEGER = 'SMALLINTEGER'
TEXT = 'TEXT'
TIME = 'TIME'
URL = 'URL'
KEY_TYPES = (
    (BIGINTEGER, _.BIGINTEGER),
    (BINARY, _.BINARY),
    (BOOLEAN, _.BOOLEAN),
    (CHAR, _.CHAR),
    (DATE, _.DATE),
    (DECIMAL, _.DECIMAL),
    (DURATION, _.DURATION),
    (EMAIL, _.EMAIL),
    (FILE, _.FILE),
    (FLOAT, _.FLOAT),
    (IMAGE, _.IMAGE),
    (INTEGER, _.INTEGER),
    (SMALLINTEGER, _.SMALLINTEGER),
    (TEXT, _.TEXT),
    (TIME, _.TIME),
    (URL, _.URL),
)


class Key(Base):
    key_type = models.CharField(
        _.key_type, max_length=20, choices=KEY_TYPES, default=CHAR
    )
    name = models.CharField(max_length=255)

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_key
        verbose_name_plural = _.vp_key
        ordering = ['name', 'key_type', '-date_create']


class ExtendGlobal(Base):
    key = models.ForeignKey(
        'mighty.key', on_delete=models.CASCADE, related_name='extend_global_key'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='extend_global_value',
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    value = models.BinaryField()

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_value
        verbose_name_plural = _.vp_value
        ordering = ['-date_create']


class Extend(Base):
    key = models.ForeignKey(
        'mighty.key', on_delete=models.CASCADE, related_name='extend_key'
    )
    object_id = models.ForeignKey(
        '', on_delete=models.CASCADE, related_name='extend_value'
    )
    value = models.BinaryField()

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_value
        verbose_name_plural = _.vp_value
        ordering = ['-date_create']
