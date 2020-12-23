from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.db.models.options import Options

from mighty.fields import JSONField
from mighty.functions import make_searchable
from mighty import translates as _
from uuid import uuid4
from sys import getsizeof

def default_logfield_dict():
    return {"emerg": {}, "alert": {}, "critical": {}, "error": {}, "warning": {}, "notice": {}, "info": {}, "debug": {}}

LIST = 'list'
EXPORT = 'export'
IMPORT = 'import'
DISABLE = 'disable'
ENABLE = 'enable'
ANTICIPATE = 'anticipate'
SOURCE = 'source'
FILTERLVL0 = 'filterlvl0'
FILTERLVL1 = 'filterlvl1'
FILTERLVL2 = 'filterlvl2'
actions = {
    LIST: _.LIST,
    DISABLE: _.DISABLE,
    ENABLE: _.ENABLE,
    EXPORT: _.EXPORT,
    IMPORT: _.IMPORT,
    ANTICIPATE: _.ANTICIPATE,
    SOURCE: _.SOURCE,
    FILTERLVL0: _.FILTERLVL0,
    FILTERLVL1: _.FILTERLVL1,
    FILTERLVL2: _.FILTERLVL2,
}
default_permissions = Options(None).default_permissions
permissions = tuple(sorted(list(actions), key=lambda x: x[0]))
class Base(models.Model):
    search_fields = []
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)
    logs = JSONField(blank=True, null=True, default=dict)
    is_disable = models.BooleanField(_.is_disable, default=False, editable=False)
    search = models.TextField(db_index=True, blank=True, null=True)
    date_create = models.DateTimeField(_.date_create, auto_now_add=True, editable=False)
    create_by = models.CharField(_.create_by, blank=True, editable=False, max_length=254, null=True)
    date_update = models.DateTimeField(_.date_update, auto_now=True, editable=False)
    update_by = models.CharField(_.update_by, blank=True, editable=False, max_length=254, null=True)
    update_count = models.PositiveBigIntegerField(default=0)
    note = models.TextField(blank=True, null=True)

    class mighty:
        perm_title = actions
        fields_str = ('__str__',)
        url_field = 'uid'

    class Meta:
        abstract = True
        default_permissions = default_permissions + permissions
        
    """
    Properties
    """

    # Model
    @property
    def app_label(self): return str(self._meta.app_label)
    @property
    def model_name(self): return str(self.__class__.__name__)
    @property
    def is_enable(self): return True if self.is_disable is False else False
    @property
    def all_permissions(self): return self._meta.default_permissions + tuple([perm[0] for perm in self._meta.permissions])

    # Admin URL
    @property
    def admin_url_args(self, config): return {"object_id": self.pk}
    @property
    def app_admin(self, reverse=None): return reverse if reverse else 'admin:%s_%s_%s'
    @property
    def admin_list_url(self): return self.get_url('changelist', self.app_admin)
    @property
    def admin_add_url(self): return self.get_url('add', self.app_admin)
    @property
    def admin_change_url(self): return self.get_url('change', self.app_admin, arguments=self.admin_url_args)
    @property
    def admin_disable_url(self): return self.get_url('disable', self.app_admin, arguments=self.admin_url_args)
    @property
    def admin_enable_url(self): return self.get_url('enable', self.app_admin, arguments=self.admin_url_args)

    # Front URL
    @property
    def url_args(self): return {self.mighty.url_field: getattr(self, self.mighty.url_field)}
    @property
    def add_url(self): return self.get_url('add')
    @property
    def list_url(self): return self.get_url('list')
    @property
    def detail_url(self): return self.get_url('view', arguments=self.url_args)
    @property
    def change_url(self): return self.get_url('change', arguments=self.url_args)
    @property
    def delete_url(self): return self.get_url('delete', arguments=self.url_args)
    @property
    def disable_url(self): return self.get_url('disable', arguments=self.url_args)
    @property
    def enable_url(self): return self.get_url('enable', arguments=self.url_args)

    # Question for disable, enable, delete
    @property
    def question_delete(self): return _d.are_you_sure_delete % self
    @property
    def question_disable(self): return _d.are_you_sure_disable % self
    @property
    def question_enable(self): return _d.are_you_sure_enable % self

    """
    Functions
    """

    # permissions
    def perm(self, perm):
        if perm in self.all_permissions:
            return '%s.%s_%s' % (str(self.app_label).lower(), perm, str(self.model_name).lower())
        return None

    # Fields facilities
    def field_config(self, field):
        return self._meta.get_field(field)

    def fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.get_fields() if field.__class__.__name__ not in excludes}

    def concrete_fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.concrete_fields if field.__class__.__name__ not in excludes}

    def related_fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.related_objects if field.__class__.__name__ not in excludes}
    
    def many_fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.many_to_many if field.__class__.__name__ not in excludes}

    # Url facilities
    def get_url_html(self, url, title):
        return format_html('<a href="%s">%s</a>' % (url, title))

    def get_url(self, action, mask="%s:%s-%s", arguments=None):
        return reverse(mask % (self.app_label.lower(), self.model_name.lower(), action), kwargs=arguments)

    # Search facilities
    def get_search_fields(self):
        return ' '.join([make_searchable(str(getattr(self, field))) for field in self.search_fields if getattr(self, field)]).split()

    def set_search(self):
        self.search = '_'+'_'.join(list(dict.fromkeys(self.get_search_fields())))

    # Log facilities
    def get_log(self, lvl, field=None):
        return self.logfields[lvl][field]

    def add_log(self, lvl, msg, field=None):
        self.logfields[lvl][field] = msg
        
    def del_log(self, lvl, field=None):
        del self.logfields[lvl][field]

    def has_log_lvl(self, lvl):
        return True if len(self.logfields[lvl]) else False

    def has_log(self):
        for lvl,errors in self.logs.items():
            if any(errors): return True
        return False

    # Create / Update
    def set_create_by(self, user):
        self.create_by = '%s.%s' % (user.id, user.username)

    def set_update_by(self, user):
        self.update_by = '%s.%s' % (user.id, user.username)

    """
    Actions
    """

    def disable(self, *args, **kwargs):
        self.is_disable = True
        self.save()

    def enable(self, *args, **kwargs):
        self.is_disable = False
        self.save()

    def save(self, *args, **kwargs):
        need_post_create = False if not self.pk else True
        self.set_search()
        if self.pk: self.update_count+=1
        super().save(*args, **kwargs)
        if need_post_create: self.post_create()

    def post_create(self):
        pass