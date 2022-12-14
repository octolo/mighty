from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.db.models.options import Options
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template import Context, Template
from django.core.exceptions import ValidationError

from mighty.functions import url_domain
from mighty.fields import JSONField
from mighty.models import fields
from mighty.functions import make_searchable, get_request_kept, get_logger, get_model

from mighty import translates as _
from uuid import uuid4
from sys import getsizeof
import copy, json

if "mighty.applications.messenger" in settings.INSTALLED_APPS:
    from mighty.applications.messenger import notify, notify_discord, notify_slack
if "mighty.applications.logger" in settings.INSTALLED_APPS:
    from mighty.applications.logger.notify.discord import DiscordLogger
    from mighty.applications.logger.notify.slack import SlackLogger

lvl_priority = ["alert", "warning", "notify", "info", "debug"]
def default_logfield_dict():
    return {lvl: {} for lvl in lvl_priority}

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
    www_action = None
    www_action_cancel = []
    search_fields = []
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)
    logs = JSONField(blank=True, null=True, default=dict)
    is_disable = models.BooleanField(_.is_disable, default=False, editable=False)
    is_immutable = models.BooleanField(default=False)
    search = models.TextField(db_index=True, blank=True, null=True)
    date_create = models.DateTimeField(_.date_create, auto_now_add=True, editable=False)
    create_by = models.CharField(_.create_by, blank=True, editable=False, max_length=254, null=True)
    date_update = models.DateTimeField(_.date_update, auto_now=True, editable=False)
    update_by = models.CharField(_.update_by, blank=True, editable=False, max_length=254, null=True)
    update_count = models.PositiveBigIntegerField(default=0)
    note = models.TextField(blank=True, null=True)
    cache = JSONField(blank=True, null=True, default=dict)
    comment = fields.CommentField(blank=True, null=True)
    use_create_by = True
    use_update_by = True
    can_notify = True
    fields_can_be_changed = "*"
    
    _logger = get_logger()
    _old_self = None
    _old_fields = None
    _history = []
    _hfirst = None
    _hlast = None
    if "mighty.applications.logger" in settings.INSTALLED_APPS:
        _discord_logger = DiscordLogger()
        _slack_logger = SlackLogger()

    @property
    def model(self):
        return type(self)

    def queryset(self):
        return type(self).objects.all()

    def history_queryset(self):
        return self.queryset().order_by('-date_create')

    @property
    def logger(self):
        return self._logger

    def make_template(self, template, context={}):
        tpl = Template(template)
        context = Context(context)
        return tpl.render(context)

    if "mighty.applications.messenger" in settings.INSTALLED_APPS:
        def notify(subject, content_type, object_id, **kwargs):
            return notify(subject, content_type, object_id, **kwargs)

        def notify_slack(hookname, **kwargs):
            return notify_slack(hookname, **kwargs)

        def notify_discord(hookname, **kwargs):
            return notify_discord(hookname, **kwargs)

    @property
    def qs_not_self(self):
        if self.pk: return self.queryset().exclude(pk=self.pk)
        return self.queryset().all()

    @property
    def history(self):
        if not len(self._history):
            self._history = self.history_queryset()
        return self._history

    @property
    def history_last(self):
        if not self._hlast:
            self._hlast = self.history.last()
        return self._hlast

    @property
    def history_first(self):
        if not self._hfirst:
            self._hfirst = self.history.first()
        return self._hfirst

    @property
    def history_not_self(self):
        if self.pk: return self.history.exclude(pk=self.pk)
        return self.history

    @property
    def _user(self):
        grk = get_request_kept()
        return grk.user if grk else None

    @property
    def can_be_changed(self):
        if self.fields_can_be_changed == "*":
            return True
        return all([field in self.fields_can_be_changed for field in self.fields_changed])

    class mighty:
        perm_title = actions
        fields_str = ('__str__',)
        url_field = 'uid'

    class Meta:
        abstract = True
        default_permissions = default_permissions + permissions

    def raise_error(self, message, code=None):
        raise ValidationError(message=message, code=code)

    def save_old_self(self):
        if self.pk and not self._old_self:
            if not self._old_fields:
                self._old_self = copy.deepcopy(self)
            else:
                self._old_self = {
                    field: getattr(self, field)
                    for field in self._old_fields
                }

    def reset_old_self(self):
        self.save_old_self()

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        self.save_old_self()

    def do_not_notify(self):
        self.can_notify = False
        
    """
    Properties
    """
    # Model
    @property
    def uid_or_pk_arg(self): return 'uid' if hastattr(self, 'uid') else 'pk'
    @property
    def uid_or_pk(self): return getattr(self, self.uid_or_pk_arg)
    @property
    def app_label(self): return str(self._meta.app_label)
    @property
    def model_name(self): return str(self.__class__.__name__)
    @property
    def is_enable(self): return True if self.is_disable is False else False
    @property
    def all_permissions(self): return self._meta.default_permissions + tuple([perm[0] for perm in self._meta.permissions])
    @property
    def cache_json(self): return json.dumps(self.cache)
    @property
    def logs_json(self): return json.dumps(self.logs)

    # Admin URL
    def url_domain(self, url): return url_domain(url)
    @property
    def admin_url_args(self): return {"object_id": self.pk}
    @property
    def app_admin(self): return 'admin:%s_%s_%s'
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

    @property
    def log_status(self):
        if self.has_log():
            for lvl in lvl_priority:
                if self.has_log_lvl(lvl):
                    return lvl
        return None


    """
    Functions
    """

    def get_has(self, attr, default=None):
        return getattr(self, attr, default) if hasattr(self, attr) else default

    def get_content_type(self):
        return ContentType.objects.get_for_model(self)

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

    def m2o_fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.related_objects if field.__class__.__name__ not in excludes}
    
    def m2m_fields(self, excludes=[]):
        return {field.name: field.__class__.__name__ for field in self._meta.many_to_many if field.__class__.__name__ not in excludes}

    # Url facilities
    def get_url_html(self, url, title):
        return format_html('<a href="%s">%s</a>' % (url, title))

    def get_url(self, action, mask="%s:%s-%s", arguments=None):
        return reverse(mask % (self.app_label.lower(), self.model_name.lower(), action), kwargs=arguments)

    # Search facilities
    def get_search_fields(self):
        return ' '.join([make_searchable(str(getattr(self, field))) for field in self.search_fields if getattr(self, field)]+self.timeline_search()).split()

    def timeline_relate(self):
        return str(self.__class__.__name__).lower() + 'timeline_set'

    def timeline_search(self):
        if hasattr(self, self.timeline_relate()):
            return [make_searchable(field.value) for field in getattr(self, self.timeline_relate()).filter(field__in=self.search_fields)]
        return []

    def set_search(self):
        self.search = '_'+'_'.join(list(dict.fromkeys(self.get_search_fields())))

    # Log facilities
    def get_log(self, lvl, field=None):
        return self.logs[lvl][field]

    def add_log(self, lvl, msg, field=None):
        if lvl not in self.logs: self.logs[lvl] = {}
        self.logs[lvl][field] = msg
        
    def del_log(self, lvl, field=None):
        del self.logs[lvl][field]

    def has_log_lvl(self, lvl):
        return True if lvl in self.logs else False

    def has_log(self):
        for lvl,errors in self.logs.items():
            if any(errors): return True
        return False

    # Cache facilities
    def add_cache(self, field, cache):
        self.cache[field] = cache

    def del_cache(self, field):
        del self.cache[field]
        
    def res_cache(self):
        self.cache = None

    def has_cache_field(self, field):
        return True if field in self.cache else False

    def has_cache(self):
        return True if self.cache and len(self.cache) else False

    # Create / Update
    @property
    def create_by_id(self):
        return self.create_by.split('.')[0]
    @property
    def update_by_id(self):
        return self.update_by.split('.')[0]
    @property
    def create_by_username(self):
        return self.create_by.split('.')[1]
    @property
    def update_by_username(self):
        return self.update_by.split('.')[1]

    @property
    def fields_changed(self):
        return (field for field in self.fields if self.property_change(field))

    def set_create_by(self, user=None):
        if user and self.use_create_by:
            self.create_by = '%s.%s' % (user.id, user.username)

    def set_update_by(self, user=None):
        if user and self.use_create_by:
            self.update_by = '%s.%s' % (user.id, user.username)

    def property_change(self, prop):
        return (not self._old_self or getattr(self._old_self, prop) != getattr(self, prop))

    def get_model(self, label, app):
        return get_model(label, app)

    """
    Actions
    """
    def disable(self, *args, **kwargs):
        self.is_disable = True
        self.save()

    def enable(self, *args, **kwargs):
        self.is_disable = False
        self.save()

    def default_data(self):
        request = get_request_kept()
        self.set_search()
        self.set_update_by(get_request_kept().user if request else None)
        if self.pk:
            self.update_count+=1
            self.www_action = "update"
            if "pre_update" not in self.www_action_cancel:
                self.pre_update()
        else:
            self.set_create_by(get_request_kept().user if request else None)
            self.www_action = "create"
            if "pre_create" not in self.www_action_cancel:
                self.pre_create()

    def save(self, *args, **kwargs):
        if self.can_be_changed:
            do_post_create = False if self.pk else True
            self.default_data()
            self.pre_save()
            super().save(*args, **kwargs)
            if do_post_create:
                if "post_create" not in self.www_action_cancel:
                    self.post_create()
            else:
                if "post_update" not in self.www_action_cancel:
                    self.post_update()
            if "post_save" not in self.www_action_cancel:
                self.post_save()
        else:
            raise self.raise_error(code="is_immutable", message="is immutable")

    def delete(self, *args, **kwargs):
        self.www_action = "delete"
        if not self.is_immutable:
            if "pre_delete" not in self.www_action_cancel:
                self.pre_delete()
            super().delete(*args, **kwargs)
            if "post_delete" not in self.www_action_cancel:
                self.post_delete()
        else:
            raise self.raise_error(code="is_immutable", message="is immutable")
 
    def pre_save(self):
        pass

    def post_save(self):
        pass

    def pre_create(self):
        pass

    def pre_update(self):
        pass

    def pre_delete(self):
        pass

    def post_create(self):
        pass

    def post_update(self):
        pass

    def post_delete(self):
        pass