from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from mighty import fields, translates as _
from mighty.applications.user.apps import UserConfig
from mighty.applications.user.forms import UserCreationForm
from mighty.admin.models import BaseAdmin
from mighty.applications.user.choices import METHOD_BACKEND
from mighty.applications.user import fields
from mighty.applications.address.admin import AddressAdminInline
from mighty.applications.user.apps import UserConfig

from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

class EmailAdmin(admin.TabularInline):
    fields = ('email', 'default')
    extra = 0

class PhoneAdmin(admin.TabularInline):
    formfield_overrides = {PhoneNumberField: {'widget': PhoneNumberPrefixWidget}}
    fields = ('phone', 'default')
    extra = 0

class InternetProtocolAdmin(admin.TabularInline):
    fields = ('ip',)
    readonly_fields = ('ip',)
    extra = 0

class UserAgentAdmin(admin.TabularInline):
    fields = ('useragent',)
    readonly_fields = ('useragent',)
    extra = 0

class UserAddressAdminInline(AddressAdminInline): pass

class UserAdmin(UserAdmin, BaseAdmin):
    formfield_overrides = {PhoneNumberField: {'widget': PhoneNumberPrefixWidget}}
    add_form = UserCreationForm
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': (UserConfig.Field.username,) + UserConfig.Field.required + ('password1', 'password2')}),)
    readonly_fields = ('method', 'channel')

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]['fields'] += ('phone', 'style')
        if UserConfig.ForeignKey.optional:
            self.fieldsets[1][1]['fields'] += ('optional',)
        self.add_field(_.informations, ('method', 'channel'))
        if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
            self.fieldsets[1][1]['fields'] += ('nationalities',)
            self.filter_horizontal += ('nationalities',)

    def save_model(self, request, obj, form, change):
        if not change: obj.method = METHOD_BACKEND
        super().save_model(request, obj, form, change)

class InvitationAdmin(BaseAdmin):
    raw_id_fields = ('user',)
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.invitation}),)
    list_display = ('__str__', 'status', 'user')
    list_filter = ('status',)
    search_fields = ('last_name', 'first_name',) + tuple('user__%s' % field for field in fields.search)