from django.db import models

from mighty.applications.user.apps import UserConfig as conf
from mighty.models import Base

class InternetProtocol(models.Model):
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_ip')
    ip = models.GenericIPAddressField(editable=False)

    class Meta(Base.Meta):
        abstract = True

class UserAgent(models.Model):
    user = models.ForeignKey(conf.ForeignKey.user, on_delete=models.CASCADE, related_name='user_useragent')
    useragent = models.CharField(max_length=255, editable=False)

    class Meta(Base.Meta):
        abstract = True


