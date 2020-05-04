"""
Model class
Add [is_disable] field at the model
This model add new permissions
- can enable
- can disable
a deactivated object is similar to a deleted object but the data remains in the database

(disable) set is_disable at True
(disable_url_html) return the link html to disable
(question_disable) return disable question
(disable_url) return the url disable
(enable) set is_disable at False
(is_enable) return bool if is_enable
(enable_url_html) return the link html to enable
(question_enable) return enable question
(enable_url) return the url enable
"""
from django.db import models
from mighty.translates import fields as _, descriptions as _d
from mighty.models.base import title, permissions

PERM_DISABLE = 'disable'
PERM_ENABLE = 'enable'
title.update({PERM_DISABLE: _.PERM_DISABLE, PERM_ENABLE: _.PERM_ENABLE})
permissions += (PERM_DISABLE, PERM_ENABLE)
class Disable(models.Model):
    is_disable = models.BooleanField(_.is_disable, default=False, editable=False)
    Qisdisable = models.Q(is_disable=False)
    Qisenable = models.Q(is_disable=True)
    title = title

    class Meta:
        abstract = True
        default_permissions = permissions

    def disable(self, *args, **kwargs):
        self.is_disable = True
        self.save()
    @property
    def disable_url_html(self): return self.get_url_html('disable', self.title['disable'])
    @property
    def question_disable(self): return _d.are_you_sure_disable % self
    @property
    def disable_url(self):
        return self.get_url('disable', arguments={"uid": self.uid}) if hasattr(self, 'uid') else self.get_url('disable', arguments={"pk": self.pk})

    def enable(self, *args, **kwargs):
        self.is_disable = False
        self.save()
    @property
    def is_enable(self): return True if self.is_disable is False else False
    @property
    def enable_url_html(self): return self.get_url_html('enable', self.title['enable'])
    @property
    def question_enable(self): return _d.are_you_sure_enable % self
    @property
    def enable_url(self):
        if hasattr(self, 'uid'):
            return self.get_url('enable', arguments={"uid": self.uid})
        return self.get_url('enable', arguments={"pk": self.pk})