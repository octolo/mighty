from django.conf import settings
from django.db import connection

try:
    from django.db.models import JSONField
except Exception:
    from jsonfield import JSONField
#if 'ckeditor' in settings.INSTALLED_APPS: from ckeditor.fields import RichTextField
#elif 'tinymce' in settings.INSTALLED_APPS: from tinymce.models import HTMLField as RichTextField

# Fields mighty
base = ('uid', 'is_disable', 'date_create', 'create_by', 'date_update', 'update_by', 'search')
logfield = ('alerts',)
image = ('image',)
image_url = ('image_url',)
source = ('sources',)
keywords = ('keywords',)
file = ('file',)
file_name = ('filename',)
news = ('title', 'news', 'date_news')

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
admin_add_url = ('admin_add_url'),
admin_list_url = ('admin_list_url'),
admin_change_url = ('admin_change_url'),
admin_delete_url = ('admin_delete_url'),
admin_disable_url = ('admin_disable_url'),
admin_enable_url = ('admin_enable_url'),

channels = ('channel_name', 'channel_type', 'from_id', 'objs', 'history')