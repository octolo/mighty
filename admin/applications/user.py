from django.contrib import admin

from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin

from mighty.models.applications.user import User, Email, Phone, InternetProtocol
from mighty.applications.user.admin import UserAdmin, EmailAdmin, PhoneAdmin, InternetProtocolAdmin

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_filter = ('content_type',)

class EmailAdmin(EmailAdmin):
    model = Email

class PhoneAdmin(PhoneAdmin):
    model = Phone

class InternetProtocolAdmin(InternetProtocolAdmin):
    model = InternetProtocol

@admin.register(User)
class UserAdmin(UserAdmin):

    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [EmailAdmin, PhoneAdmin, InternetProtocolAdmin]
        return super(UserAdmin, self).change_view(*args, **kwargs)
