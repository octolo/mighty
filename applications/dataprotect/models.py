from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify
from mighty.fields import JSONField
from mighty.models.base import Base
from mighty.applications.dataprotect import choices as _c

class ServiceData(Base):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=15, choices=_c.CATEGORY, default=_c.STRICTLY)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)

    class Meta(Base.Meta):
        abstract = True

    @property
    def level_desc(self):
        return getattr(_c, "%s_DESC" % self.level)

    def set_code(self):
        if not self.code:
            self.code = slugify(self.name)

    def pre_save(self):
        self.set_code()

    def as_json(self):
        return {
            "name": self.name,
            "category": self.category,
            "code": self.code,
        }

class UserDataProtect(Base):
    session_id = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    accept = models.ManyToManyField("mighty.ServiceData", blank=True, related_name="accept_service_data")
    refuse = models.ManyToManyField("mighty.ServiceData", blank=True, related_name="refuse_service_data")

    class Meta(Base.Meta):
        abstract = True

    def __str__(self):
        return "%s (%s/%s)" % (str(self.user), str(self.nbr_accept), str(self.nbr_refuse))

    @property
    def nbr_accept(self):
        return self.accept.count()

    @property
    def nbr_refuse(self):
        return self.refuse.count()