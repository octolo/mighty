from django.db import models
from mighty.models.uid import Uid

EMERG = 0
ALERT = 1
CRITICAL = 2
ERROR = 3
WARNING = 4
NOTICE = 5
INFO = 6
DEBUG = 7
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
class Log(Uid):
    date = models.DateTimeField(auto_now_add=True, editable=False)
    code = models.SmallPositiveIntegerField(choices=LEVEL_CHOICES, default=DEBUG, editable=False)
    message = models.TextField(editable=False)
    user = models.PositiveIntegerField(blank=True, editable=False, null=True)

