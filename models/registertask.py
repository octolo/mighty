from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from mighty.models.base import Base
from mighty import choices as _c
from mighty.decorators import NamedIdModel

TYPE_REMIND = "REMIND"
TYPE_ALERT = "ALERT"
TYPE_REPORTING = "REPORTING"
TYPE_OTHER = "OTHER"
CHOICES_TYPE = (
    (TYPE_REMIND, _("remind")),
    (TYPE_ALERT, _("alert")),
    (TYPE_REPORTING, _("reporting")),
    (TYPE_OTHER, _("other")),
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

@NamedIdModel(fields=["name"])
class RegisterTask(Base):
    name = models.CharField(max_length=255, unique=True)
    desc = models.TextField(blank=True, null=True)
    register_type = models.CharField(max_length=10, choices=CHOICES_TYPE, default=TYPE_ALERT)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="registertask_to_content_type")
    is_enable_test = models.TextField(blank=True, null=True)
    how_start_task = models.TextField()

    class Meta(Base.Meta):
        abstract = True
        ordering = ("content_type", "date_create",)

    @property
    def name_or_how(self):
        return self.name or self.how_start_task

    def __str__(self):
        return self.name_or_how

    def pre_save(self):
        self.set_named_id()

class RegisterTaskSubscription(Base):
    register = models.ForeignKey("mighty.RegisterTask", on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=_c.CHOICES_STATUS, default=_c.STATUS_INITIALIZED)
    last_date_task = models.DateTimeField(auto_now_add=True)
    period = models.CharField(max_length=10, choices=CHOICES_PERIOD, default=PERIOD_EVERYDAY)
    choiceday = models.CharField(max_length=10, choices=CHOICES_DAY, blank=True, null=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)

    content_type_subscriber = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, related_name="registertask_to_subscriber")
    object_id_subscriber = models.PositiveIntegerField(null=True, blank=True)
    content_object_subscriber = GenericForeignKey('content_type_subscriber', 'object_id_subscriber')

    class Meta(Base.Meta):
        abstract = True
        ordering = ("date_create", "last_date_task")

    @property
    def content_object(self):
        if self.object_id:
            return self.register.content_type.get_object_for_this_type(id=self.object_id)
        return self.register.content_type

    @property
    def subscriber(self):
        return self.content_object_subscriber

    @property
    def subscribe_to(self):
        return self.content_object

    @property
    def is_delta_date_ok(self):
        return True

    @property
    def is_register_enable(self):
        if self.object_id and hasattr(self.content_object, self.register.is_enable_test):
                enable = getattr(self.content_object, self.register.is_enable_test)
                return enable() if callable(enable) else enable
        return True

    def start_task(self):
        if self.is_register_enable:
            if self.is_delta_date_ok:
                try:
                    self._logger.info("start register task - sub: %s, model: %s, object_id: %s" % (self.pk, self.register, self.object_id))
                    getattr(self.content_object, self.register.how_start_task)(self.subscriber)
                    self.status = _c.STATUS_FINISHED
                    self.last_date_task = timezone.now()
                except Exception:
                    self.status = _c.STATUS_ERROR
                    self._logger.warning("register task can't be started - sub: %s, model: %s, object_id: %s" % (self.pk, self.register, self.object_id))
        else:
            self.status = _c.STATUS_EXPIRED
            self.last_date_task = timezone.now()
        self.save()
