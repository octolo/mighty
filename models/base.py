from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from mighty.fields import JSONField
from mighty.functions import make_searchable
from mighty import translates as _
from uuid import uuid4

def default_logfield_dict():
    return {"emerg": {}, "alert": {}, "critical": {}, "error": {}, "warning": {}, "notice": {}, "info": {}, "debug": {}}

ADD = 'add'
DETAIL = 'detail'
LIST = 'list'
CHANGE = 'change'
DELETE = 'delete'
EXPORT = 'export'
IMPORT = 'import'
DISABLE = 'disable'
ENABLE = 'enable'
FILTERLVL0 = 'filter_lvl0'
FILTERLVL1 = 'filter_lvl1'
FILTERLVL2 = 'filter_lvl2'
CHOICES_PERMISSIONS = {
    ADD: _.ADD,
    LIST: _.LIST,
    DETAIL: _.DETAIL,
    CHANGE: _.CHANGE,
    DELETE: _.DELETE,
    DISABLE: _.DISABLE,
    ENABLE: _.ENABLE,
    EXPORT: _.EXPORT,
    IMPORT: _.IMPORT,
    FILTERLVL0: _.FILTERLVL0,
    FILTERLVL1: _.FILTERLVL1,
    FILTERLVL2: _.FILTERLVL2,
}
PERMISSIONS = sorted(list(CHOICES_PERMISSIONS), key=lambda x: x[0])
class Base(models.Model):
    search_fields = []
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)
    logfields = JSONField(blank=True, null=True, default=default_logfield_dict)
    is_disable = models.BooleanField(_.is_disable, default=False, editable=False)
    search = models.TextField(db_index=True, blank=True, null=True)
    date_create = models.DateTimeField(_.date_create, auto_now_add=True, editable=False)
    create_by = models.CharField(_.create_by, blank=True, editable=False, max_length=254, null=True)
    date_update = models.DateTimeField(_.date_update, auto_now=True, editable=False)
    update_by = models.CharField(_.update_by, blank=True, editable=False, max_length=254, null=True)

    class mighty:
        perm_title = CHOICES_PERMISSIONS
        fields_str = ('__str__',)
        url_field = 'uid'

    class Meta:
        abstract = True
        default_permissions = PERMISSIONS
        
    """
    Properties
    """

    @property
    def app_label(self): return str(self._meta.app_label)
    @property
    def model_name(self): return str(self.__class__.__name__)
    @property
    def admin_list_url(self): return self.get_url('changelist', 'admin:%s_%s_%s')
    @property
    def admin_add_url(self): return self.get_url('add', 'admin:%s_%s_%s')
    @property
    def admin_change_url(self): return self.get_url('change', 'admin:%s_%s_%s', arguments={"object_id": self.pk})
    @property
    def admin_disable_url(self): return self.get_url('disable', 'admin:%s_%s_%s', arguments={"object_id": self.pk})
    @property
    def admin_enable_url(self): return self.get_url('enable', 'admin:%s_%s_%s', arguments={"object_id": self.pk})
    @property
    def add_url(self): return self.get_url('add')
    @property
    def list_url(self): return self.get_url('list')
    @property
    def detail_url(self): return self.get_url('detail', arguments=self.arguments())
    @property
    def change_url(self): return self.get_url('change', arguments=self.arguments())
    @property
    def delete_url(self): return self.get_url('delete', arguments=self.arguments())
    @property
    def add_url_html(self): return self.get_url(self.get_url('add'), self.title['add'])
    @property
    def list_url_html(self): return self.get_url_html(self.get_url('list'), self.title['list'])
    @property
    def detail_url_html(self): return self.get_url_html(self.get_url('detail', arguments=self.arguments()), self.title['detail'])
    @property
    def change_url_html(self): return self.get_url_html(self.get_url('change', arguments=self.arguments()), self.title['change'])
    @property
    def delete_url_html(self): return self.get_url_html(self.get_url('delete', arguments=self.arguments()), self.title['delete'])
    @property
    def question_delete(self): return _d.are_you_sure_delete % self
    @property
    def disable_url_html(self): return self.get_url_html('disable', self.title['disable'])
    @property
    def question_disable(self): return _d.are_you_sure_disable % self
    @property
    def disable_url(self): return self.get_url('disable', arguments=self.arguments())
    @property
    def is_enable(self): return True if self.is_disable is False else False
    @property
    def enable_url_html(self): return self.get_url_html('enable', self.title['enable'])
    @property
    def question_enable(self): return _d.are_you_sure_enable % self
    @property
    def enable_url(self): return self.get_url('enable', arguments=self.arguments())

    """
    Functions
    """
    def perm(self, perm):
        return '%s.%s_%s' % (str(self.app_label).lower(), perm, str(self.model_name).lower())

    def fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.get_fields() if field.__class__.__name__ not in excludes}

    def get_url_html(self, url, title):
        return format_html('<a href="%s">%s</a>' % (url, title))

    def get_url(self, action, mask="%s:%s-%s", arguments=None):
        return reverse(mask % (self.app_label.lower(), self.model_name.lower(), action), kwargs=arguments)

    def arguments(self):
        return {self.mighty.url_field: getattr(self, self.mighty.url_field)}

    def disable(self, *args, **kwargs):
        self.is_disable = True
        self.save()

    def enable(self, *args, **kwargs):
        self.is_disable = False
        self.save()

    def get_search(self):
        return make_searchable(str(' '.join([str(getattr(self, field)) for field in self.search_fields])))

    def set_search(self):
        self.search = self.get_search()

    def get_logfield(self, lvl, field):
        return self.logfields[lvl][field]

    def add_logfield(self, lvl, field, msg):
        self.logfields[lvl][field] = msg

    def is_in_logfield(self, lvl):
        return True if len(self.logfields[lvl]) else False

    def logfield_html(self, lvl, field):
        alert = ['<div class="%s">' % lvl,
            """<span class="closebtn-logfield" onclick="this.parentElement.style.display='none';">""",
            '&times;</span>%s</div>' % self.logfields[lvl][field],]        
        return  format_html("".join(alert))

    def save(self, *args, **kwargs):
        self.set_search()
        super().save(*args, **kwargs)