from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session

from mighty.apps import MightyConfig as conf
from mighty.admin.site import AdminSite
from mighty import fields, models as all_models
from mighty.admin.models import BaseAdmin

mysite = AdminSite()
admin.site = mysite
admin.sites.site = mysite

###########################
# Models django
###########################
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_filter = ('content_type',)
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']

###########################
# Models in mighty
###########################
@admin.register(all_models.Backend)
class BackendAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.backend}),)
    list_display = ('service', 'content_type', 'is_disable')
    search_fields = ('service',)
@admin.register(all_models.Reporting)
class ReportingAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.reporting}),)
    list_display = ('name', 'content_type', 'target')
    search_fields = ('service',)


@admin.register(all_models.ConfigClient)
class ConfigClientAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('name', 'config')}),)
    list_display = ('name',)
    readonly_fields = ('url_name',)

@admin.register(all_models.ConfigSimple)
class ConfigSimpleAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('name', 'configchar', 'configbool', 'is_boolean')}),)
    list_display = ('name',)
    readonly_fields = ('url_name',)

@admin.register(all_models.TemplateVariable)
class TemplateVariableAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('name', 'description', 'content_type', 'template', 'hidden')}),)
    list_display = ('name', 'description', 'content_type', 'hidden')

if hasattr(settings, 'CHANNEL_LAYERS'):
    @admin.register(all_models.Channel)
    class ChannelAdmin(BaseAdmin):
        list_display = ('channel_name', 'channel_type', 'date_update')
        fieldsets = ((None, {'classes': ('wide',), 'fields': fields.channels}),)
        search_fields = ('channel_name', 'channel_type',)
        view_on_site = False

class NewsAdmin(admin.StackedInline):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': fields.news + ('keywords',)}),)
    extra = 0

###########################
# Models apps mighty
###########################

# Nationality
if 'mighty.applications.logger' in settings.INSTALLED_APPS:
    from mighty.applications.logger import admin as admin_logger
    @admin.register(all_models.Log)
    class LogAdmin(admin_logger.LogAdmin): pass
    @admin.register(all_models.ModelChangeLog)
    class ModelChangeLogAdmin(admin_logger.ModelChangeLogAdmin): pass

# Nationality
if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    from mighty.applications.nationality import admin as admin_nationality
    @admin.register(all_models.Nationality)
    class NationalityAdmin(admin_nationality.NationalityAdmin): pass
    class TranslateDictAdmin(admin_nationality.TranslateDictAdmin): model = all_models.TranslateDict
    @admin.register(all_models.Translator)
    class TranslateDictAdmin(admin_nationality.TranslatorAdmin):
        inlines = [TranslateDictAdmin]

# Messenger
if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
    from mighty.applications.messenger import admin as admin_messenger
    @admin.register(all_models.Missive)
    class NationalityAdmin(admin_messenger.MissiveAdmin): pass
    @admin.register(all_models.Notification)
    class NotificationAdmin(admin_messenger.NotificationAdmin): pass
    @admin.register(all_models.Template)
    class NotificationAdmin(admin_messenger.TemplateAdmin): pass

# User
if 'mighty.applications.user' in settings.INSTALLED_APPS:
    from mighty.applications.user import admin as admin_user
    from mighty.applications.user.apps import UserConfig as user_conf

    class UserEmailAdmin(admin_user.UserEmailAdmin): model = all_models.UserEmail
    class UserPhoneAdmin(admin_user.UserPhoneAdmin): model = all_models.UserPhone
    class InternetProtocolAdmin(admin_user.InternetProtocolAdmin): model = all_models.InternetProtocol
    class UserAgentAdmin(admin_user.UserAgentAdmin): model = all_models.UserAgent
    class UserAddressAdmin(admin_user.UserAddressAdminInline): model = all_models.UserAddress
    class UserAdmin(admin_user.UserAdmin): pass

    if 'mighty.applications.logger' in settings.INSTALLED_APPS:
        from mighty.applications.logger.admin import ModelWithLogAdmin
        class UserAdmin(UserAdmin, ModelWithLogAdmin): pass

    @admin.register(all_models.User)
    class UserAdmin(UserAdmin):
        view_on_site = False

        def add_view(self, *args, **kwargs):
            self.inlines = []
            return super(admin_user.UserAdmin, self).add_view(*args, **kwargs)

        def change_view(self, *args, **kwargs):
            self.inlines = [UserEmailAdmin, UserPhoneAdmin, InternetProtocolAdmin, UserAgentAdmin, UserAddressAdmin]
            return super(admin_user.UserAdmin, self).change_view(*args, **kwargs)

    @admin.register(all_models.Invitation)
    class InvitationAdmin(admin_user.InvitationAdmin): pass

    if user_conf.protect_trashmail:
        @admin.register(all_models.Trashmail)
        class TrashmailAdmin(admin_user.TrashmailAdmin): pass

# Data protect
if 'mighty.applications.dataprotect' in settings.INSTALLED_APPS:
    from mighty.applications.dataprotect import admin as admin_dataprotect
    @admin.register(all_models.ServiceData)
    class ServiceDataAdmin(admin_dataprotect.ServiceDataAdmin): pass
    @admin.register(all_models.UserDataProtect)
    class UserDataProtectAdmin(admin_dataprotect.UserDataProtectAdmin): pass

# Twofactor
if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
    from mighty.applications.twofactor import admin as admin_twofactor
    @admin.register(all_models.Twofactor)
    class TwofactorAdmin(admin_twofactor.TwofactorAdmin): pass

# Shop
if 'mighty.applications.shop' in settings.INSTALLED_APPS:
    from mighty.applications.shop import admin as admin_shop
    @admin.register(all_models.ShopService)
    class ShopServiceAdmin(admin_shop.ServiceAdmin): pass
    @admin.register(all_models.ShopItem)
    class ShopItemAdmin(admin_shop.ItemAdmin): pass
    @admin.register(all_models.Offer)
    class OfferAdmin(admin_shop.OfferAdmin): pass
    @admin.register(all_models.Subscription)
    class SubscriptionAdmin(admin_shop.SubscriptionAdmin): pass
    @admin.register(all_models.Bill)
    class BillAdmin(admin_shop.BillAdmin): pass
    @admin.register(all_models.Discount)
    class DiscountAdmin(admin_shop.DiscountAdmin): pass
    @admin.register(all_models.PaymentMethod)
    class PaymentMethodAdmin(admin_shop.PaymentMethodAdmin): pass
    @admin.register(all_models.SubscriptionRequest)
    class SubscriptionRequestAdmin(admin_shop.SubscriptionRequestAdmin): pass

if conf.enable_mimetype:
    from mighty.models import MimeType
    @admin.register(MimeType)
    class MimeTypeAdmin(BaseAdmin):
        view_on_site = False

#if 'mighty.applications.grapher' in settings.INSTALLED_APPS:
#    from mighty.admin.applications import grapher

#from django.apps import apps
#apps.get_model('auth.Group')._meta.app_label = 'mighty'
#apps.get_model('auth.Group')._meta.db_table = 'mighty_group'
#apps.get_model('auth.Permission')._meta.app_label = 'mighty'
#apps.get_model('auth.Permission')._meta.db_table = 'mighty_permission'

#def render_change_form(self, request, context, *args, **kwargs):
#    if hasattr(kwargs['obj'], 'company'):
#        replace_args = {"company": kwargs['obj'].company}
#        if kwargs['obj'].sql_date_start is not None:
#            replace_args["sql_date_start__lte"] = kwargs['obj'].sql_date_start
#        context['adminform'].form.fields['replace'].queryset = context['adminform'].form.fields['replace'].queryset.filter(**replace_args)
#        resolution_args = {"assembly__company": kwargs['obj'].company}
#        context['adminform'].form.fields['resolution'].queryset = context['adminform'].form.fields['resolution'].queryset.filter(**resolution_args)
#        ag_leave_args = {"company": kwargs['obj'].company}
#        if kwargs['obj'].resolution is not None:
#            ag_leave_args["date_assembly__gt"] = kwargs['obj'].resolution.assembly.date_assembly
#        context['adminform'].form.fields['ag_leave'].queryset = context['adminform'].form.fields['ag_leave'].queryset.filter(**ag_leave_args)
#    else:
#        context['adminform'].form.fields['replace'].queryset = context['adminform'].form.fields['resolution'].queryset.none()
#        context['adminform'].form.fields['resolution'].queryset = context['adminform'].form.fields['resolution'].queryset.none()
#        context['adminform'].form.fields['ag_leave'].queryset = context['adminform'].form.fields['ag_leave'].queryset.none()
#    return super(MandateAdmin, self).render_change_form(request, context, *args, **kwargs)

#def get_form(self, request, obj=None, **kwargs):
#    request._obj_ = obj
#    return super(MandateAdmin, self).get_form(request, obj, **kwargs)

#def __init__(self, model, admin_site):
#    super().__init__(model, admin_site)

#def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
#    field = super(MandateAGDataAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#    if db_field.name == 'assembly':
#        if request._obj_:
#            args = {"company": request._obj_.company}
#            if request._obj_.resolution is not None:
#                args["date_assembly__gte"] = request._obj_.resolution.assembly.date_assembly
#            field.queryset = field.queryset.filter(**args)
#        else: field.queryset = field.queryset.none()
#    if db_field.name == 'renewal':
#        if request._obj_:
#            args = {"assembly__company": request._obj_.company}
#            if request._obj_.resolution is not None:
#                args["assembly__date_assembly__gte"] = request._obj_.resolution.assembly.date_assembly
#            field.queryset = field.queryset.filter(**args)
#        else: field.queryset = field.queryset.none()
#    if db_field.name == 'revocation':
#        if request._obj_:
#            args = {"assembly__company": request._obj_.company}
#            if request._obj_.resolution is not None:
#                args["assembly__date_assembly__gte"] = request._obj_.resolution.assembly.date_assembly
#            field.queryset = field.queryset.filter(**args)
#        else: field.queryset = field.queryset.none()
#    return field
