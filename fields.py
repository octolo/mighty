from django.conf import settings
from django.db.models import TextField

try:
    from django.db.models import JSONField
except Exception:
    from jsonfield import JSONField  # noqa


def RichTextField(*args, **kwargs):
    if 'django_ckeditor_5' in settings.INSTALLED_APPS:
        from django_ckeditor_5.fields import CKEditor5Field

        return CKEditor5Field(*args, **kwargs)
    return TextField(*args, **kwargs)


# Fields mighty
uid = ('uid',)
is_disable = ('is_disable',)
date_create = ('date_create',)
create_by = ('create_by',)
date_update = ('date_update',)
update_by = ('update_by',)
search = ('search',)
update_count = ('update_count',)
logfield = ('alerts',)
image = ('image',)
image_url = ('image_url',)
source = ('sources',)
keywords = ('keywords',)
file = ('file',)
file_name = ('filename',)
task = ('task_list', 'task_status')

base = (
    'uid',
    'is_disable',
    'is_immutable',
    'date_create',
    'create_by',
    'date_update',
    'update_by',
    'search',
    'update_count',
    'cache',
    'logs',
)

news = ('title', 'news', 'date_news')

_file = (
    'file',
    'filename',
    'filemimetype',
    'charset',
    'extracontenttype',
    'metadata',
    'size',
    'thumbnail',
)

# URL
file_url = ('file_url',)
downlad_url = ('download_url',)
pdf_url = ('pdf_url',)
add_url = ('add_url',)
list_url = ('list_url',)
detail_url = ('detail_url',)
change_url = ('change_url',)
delete_url = ('delete_url',)
disable_url = ('disable_url',)
enable_url = ('enable_url',)
export_url = ('export_url',)
import_url = ('import_url',)

# Admin URL
admin_add_url = (('admin_add_url'),)
admin_list_url = (('admin_list_url'),)
admin_change_url = (('admin_change_url'),)
admin_delete_url = (('admin_delete_url'),)
admin_disable_url = (('admin_disable_url'),)
admin_enable_url = (('admin_enable_url'),)

channels = ('channel_name', 'channel_type', 'from_id', 'objs', 'history')

backend = (
    'service',
    'content_type',
    'backend',
    'backend_list',
)

# Decorators

immutable = (
    'immutable',
    'immutable_delete',
    'immutable_fields',
)

reporting = (
    'name',
    'file_name',
    'content_type',
    'target',
    'manager',
    'config',
    'filter_config',
    'filter_related',
    'filter_request',
    'is_detail',
    'can_excel',
    'cfg_excel',
    'can_csv',
    'cfg_csv',
    'can_pdf',
    'cfg_pdf',
    'html_pdf',
    'email_html',
)

registertask = (
    'named_id',
    'name',
    'desc',
    'register_type',
    'content_type',
    'is_enable_test',
    'how_start_task',
)

registertasksubscription = (
    'register',
    'status',
    'period',
    'choiceday',
    'last_date_task',
    'object_id',
    'content_type_subscriber',
    'object_id_subscriber',
)
