from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin

from mighty.models.applications.user import ProxyUser, Email, Phone, InternetProtocol, UserAgent, UserAddress
from mighty.applications.user.admin import UserAdmin, EmailAdmin, PhoneAdmin, InternetProtocolAdmin, UserAgentAdmin

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_filter = ('content_type',)

class EmailAdmin(EmailAdmin):
    model = Email

class PhoneAdmin(PhoneAdmin):
    model = Phone

class InternetProtocolAdmin(InternetProtocolAdmin):
    model = InternetProtocol

class UserAgentAdmin(UserAgentAdmin):
    model = UserAgent

if 'mighty.applications.address' in settings.INSTALLED_APPS:
    from mighty.applications.address.admin import AddressAdminInline
    class UserAdminInline(AddressAdminInline):
        model = UserAddress

@admin.register(ProxyUser)
class UserAdmin(UserAdmin):
    view_on_site = False
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [EmailAdmin, PhoneAdmin, InternetProtocolAdmin, UserAgentAdmin]
        if 'mighty.applications.address' in settings.INSTALLED_APPS:
            self.inlines.append(UserAdminInline)
        return super(UserAdmin, self).change_view(*args, **kwargs)
