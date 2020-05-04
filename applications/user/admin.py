from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from mighty import fields
from mighty.translates import descriptions as _
from mighty.applications.user.apps import UserConfig
from mighty.applications.user.forms import UserCreationForm
from mighty.admin.models import BaseAdmin
from mighty.applications.user.models import METHOD_BACKEND

class EmailAdmin(admin.TabularInline):
    extra = 1


from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
class PhoneAdmin(admin.TabularInline):
    formfield_overrides = {PhoneNumberField: {'widget': PhoneNumberPrefixWidget}}
    extra = 1

class InternetProtocolAdmin(admin.TabularInline):
    extra = 0

class UserAdmin(UserAdmin, BaseAdmin):
    formfield_overrides = {PhoneNumberField: {'widget': PhoneNumberPrefixWidget}}
    add_form = UserCreationForm
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': (UserConfig.Field.username,) + UserConfig.Field.required + ('password1', 'password2')}),)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]['fields'] += ('phone',)

    def save_model(self, request, obj, form, change):
        if not change: obj.method = METHOD_BACKEND
        super().save_model(request, obj, form, change)