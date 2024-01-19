from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from mighty.models.base import Base
from mighty import choices as _c

TYPE_REMIND = "REMIND"
TYPE_ALERT = "ALERT"
TYPE_REPORTING = "REPORTING"
CHOICES_TYPE = (
    (TYPE_REMIND, _("remind")),
    (TYPE_ALERT, _("alert")),
    (TYPE_REPORTING, _("reporting")),
)

DAY_MONDAY = "MONDAY"
DAY_TUESDAY = "TUESDAY"
DAY_WEDNESDAY = "WEDNESDAY"
DAY_THURSDAY = "THURSDAY"
DAY_FRIDAY = "FRIDAY"
DAY_SATURDAY = "SATURDAY"
DAY_SUNDAY = "SUNDAY"
CHOICES_DAY = (
    (DAY_MONDAY, _("Monday")),
    (DAY_TUESDAY, _("Tuesday")),
    (DAY_WEDNESDAY, _("Wednesday")),
    (DAY_THURSDAY, _("Thursday")),
    (DAY_FRIDAY, _("Friday")),
    (DAY_SATURDAY, _("Saturday")),
    (DAY_SUNDAY, _("Sunday")),
)

PERIOD_MONTHLY = "MONTHLY"
PERIOD_WEEKLY = "WEEKLY"
PERIOD_3DAYS = "3DAYS"
PERIOD_2DAYS = "2DAYS"
PERIOD_CHOICEDAY = "CHOICEDAY"
PERIOD_EVERYDAY = "EVERYDAY"
CHOICES_PERIOD = (
    (PERIOD_MONTHLY, _("monthly")),
    (PERIOD_WEEKLY, _("weekly")),
    (PERIOD_3DAYS, _("every 3 days")),
    (PERIOD_2DAYS, _("every 2 days")),
    (PERIOD_CHOICEDAY, _("choose a day")),
    (PERIOD_EVERYDAY, _("every day")),
)

class RegisterTask(Base):
    register_type = models.CharField(max_length=10, choices=CHOICES_TYPE, default=TYPE_ALERT)
    status = models.CharField(max_length=11, choices=_c.CHOICES_STATUS, default=_c.STATUS_INITIALIZED)

    period = models.CharField(max_length=10, choices=CHOICES_PERIOD, default=PERIOD_EVERYDAY)
    choiceday = models.CharField(max_length=10, choices=CHOICES_DAY, blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, related_name="registertask_to_content_type")
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    is_enable_test = models.TextField()
    how_start_task = models.TextField()
    last_date_task = models.DateTimeField(auto_now_add=True)

    class Meta(Base.Meta):
        abstract = True

    @property
    def is_delta_date_ok(self):
        return True

    @property
    def is_register_enable(self):
        return getattr(self.content_object, self.is_enable_test)()

    def start_task(self):
        if self.is_register_enable:
            if self.is_delta_date_ok:
                try:
                    getattr(self.content_object, self.how_start_task)
                    self.status = _c.STATUS_FINISHED
                    self.last_date_task = timezone.now
                except Exception:
                    self.status = _c.STATUS_ERROR
        else:
            self.status = _c.STATUS_EXPIRED
            self.last_date_task = timezone.now
        self.save()
