
from django.db import models
from mighty.applications.messenger import translates as _
from mighty.applications.messenger.models.abstracts import MessengerModel
from mighty.applications.messenger.decorators import MissiveFollower
from mighty.applications.logger import choices

fields_shared = (
    "mode",
    "status",
    "priority",
    "target",
    "service",
    "denomination",
    "header_html",
    "footer_html",
    "subject",
    "html",
    "txt",
)


@MissiveFollower(related_name="missive_to_notification")
class Notification(MessengerModel):
    is_read = models.BooleanField(default=True)
    level = models.PositiveSmallIntegerField(choices=choices.LEVEL, default=choices.INFO)

    class Meta(MessengerModel.Meta):
        abstract = True
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        permissions = [('can_notify', _.permission_notify),]
        ordering = ['-date_create',]

    def need_to_send(self):
        getattr(self, 'sendnotify_%s' % self.mode.lower())()

    @property
    def data_shared(self):
        data = {field: getattr(self, field) for field in fields_shared}
        data.update({
            "content_type": self.content_type,
            "object_id": self.object_id,
        })
        return data

    def sendnotify_email(self):
        self.missive = self.model_missive(**self.data_shared)
        self.missive.save()

    def sendnotify_sms(self):
        self.missive = self.model_missive(**self.data_shared)
        self.missive.save()

    def sendnotify_web(self):
        pass

    def sendnotify_app(self):
        pass
