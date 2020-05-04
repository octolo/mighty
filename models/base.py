from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from mighty.translates import fields as _, descriptions as _d

PERM_ADD = 'add'
PERM_DETAIL = 'detail'
PERM_LIST = 'list'
PERM_CHANGE = 'change'
PERM_DELETE = 'delete'
PERM_EXPORT = 'export'
PERM_IMPORT = 'import'
title = {
    PERM_ADD: _.PERM_ADD,
    PERM_LIST: _.PERM_LIST,
    PERM_DETAIL: _.PERM_DETAIL,
    PERM_CHANGE: _.PERM_CHANGE,
    PERM_DELETE: _.PERM_DELETE,
    PERM_EXPORT: _.PERM_EXPORT,
    PERM_IMPORT: _.PERM_IMPORT}
permissions = (PERM_ADD, PERM_DETAIL, PERM_LIST, PERM_CHANGE, PERM_DELETE, PERM_EXPORT, PERM_IMPORT)
class Base(models.Model):
    date_create = models.DateTimeField(_.date_create, auto_now_add=True, editable=False)
    date_update = models.DateTimeField(_.date_update, auto_now=True, editable=False)
    update_by = models.CharField(_.update_by, blank=True, editable=False, max_length=254, null=True)
    title = title

    class Ajax:
        fields_str = ('__str__',)

    class Meta:
        abstract = True
        default_permissions = permissions

    def save(self, *args, **kwargs):
        if hasattr(self, "cleaner"): self.cleaner()
        super().save(*args, **kwargs)

    def perm(self, perm):
        return '%s.%s_%s' % (str(self.app_label).lower(), perm, str(self.model_name).lower())

    def fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.get_fields() if field.__class__.__name__ not in excludes}

    def get_url_html(self, url, title):
        return format_html('<a href="%s">%s</a>' % (url, title))

    def get_url(self, action, mask="%s:%s-%s", arguments=None):
        return reverse(mask % (self.app_label.lower(), self.model_name.lower(), action), kwargs=arguments)

    @property
    def app_label(self): return str(self._meta.app_label)
    @property
    def model_name(self): return str(self.__class__.__name__)
    @property
    def admin_list_url(self): return self.get_url('changelist', 'admin:%s_%s_%s')
    @property
    def admin_add_url(self): return self.get_url('add''admin:%s_%s_%s')
    @property
    def admin_change_url(self): return self.get_url('change', 'admin:%s_%s_%s', arguments={"object_id": self.pk})
    @property
    def add_url(self): return self.get_url('add')
    @property
    def list_url(self): return self.get_url('list')
    @property
    def detail_url(self): return self.get_url('detail', arguments={"pk": self.pk})
    @property
    def change_url(self): return self.get_url('change', arguments={"pk": self.pk})
    @property
    def delete_url(self): return self.get_url('delete', arguments={"pk": self.pk})
    @property
    def add_url_html(self): return self.get_url(self.get_url('add'), self.title['add'])
    @property
    def list_url_html(self): return self.get_url_html(self.get_url('list'), self.title['list'])
    @property
    def detail_url_html(self): return self.get_url_html(self.get_url('detail', arguments={"pk": self.pk}), self.title['detail'])
    @property
    def change_url_html(self): return self.get_url_html(self.get_url('change', arguments={"pk": self.pk}), self.title['change'])
    @property
    def delete_url_html(self): return self.get_url_html(self.get_url('delete', arguments={"pk": self.pk}), self.title['delete'])
    @property
    def question_delete(self): return _d.are_you_sure_delete % self