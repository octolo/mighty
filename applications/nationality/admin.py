
from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from mighty.fields import JSONField
from mighty.admin.models import BaseAdmin
from mighty.applications.nationality import fields

class NationalityAdmin(BaseAdmin):
    view_on_site = False
    list_display = ('country', 'image_html', 'alpha2', 'alpha3', 'numeric')
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.nationality}),)

class TranslateDictAdmin(admin.StackedInline):
    formfield_overrides = {JSONField: {'widget': JSONEditorWidget},}
    fields = fields.translatedict
    extra = 0

class TranslatorAdmin(BaseAdmin):
    view_on_site = False
    list_display = ('name',)
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('name',)}),)