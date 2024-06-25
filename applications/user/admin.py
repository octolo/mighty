from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from mighty import fields, translates as _
from mighty.applications.user.apps import UserConfig
from mighty.applications.user.forms import UserCreationForm, UserMergeAccountsAdminForm, UserChangeForm
from mighty.admin.models import BaseAdmin
from mighty.applications.user.choices import METHOD_BACKEND
from mighty.applications.user import fields
from mighty.applications.address.admin import AddressAdminInline
from mighty.applications.address import fields as address_fields
from mighty.applications.user.apps import UserConfig
from mighty.applications.messenger.decorators import AdminMissivesView
from mighty.decorators import AdminRegisteredTasksView
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from mighty.applications.user import get_form_fields
from django.forms.models import BaseInlineFormSet
from django import forms

if apps.is_installed('allauth'):
    from allauth.account.models import EmailAddress

    class UserEmailAdminFormset(BaseInlineFormSet):
        def save(self, commit=True):
            instances = super().save(commit=False)
            for form in self.forms:
                # Check if the form has changes and one of them is the 'primary' field
                if form.has_changed() and 'primary' in form.changed_data:
                    # Change user.email to the new primary email
                    if form.cleaned_data['primary']:
                        form.instance.user.email = form.instance.email
                        form.instance.user.save()
                        # invoke EmailAddress.set_as_primary() method
                        form.instance.set_as_primary()
            if commit:
                for instance in instances:
                    instance.save()
                self.save_m2m()

            return instances

    class UserEmailAdminForm(forms.ModelForm):
        class Meta:
            model = EmailAddress
            fields = '__all__'

        def save(self, commit=True):
            instance = super().save(commit=False)
            if commit:
                instance.save()
            return instance

        def clean_email(self):
            email = self.cleaned_data["email"]
            return get_user_model().validate_unique_email(email, self.instance.user_id)

    class UserEmailAdmin(admin.TabularInline):
        form = UserEmailAdminForm
        extra = 1
        can_delete = True
        fields = ['email', 'verified', 'primary']  #
        raw_id_fields = ("user",)
        model = EmailAddress
        formset = UserEmailAdminFormset
else:
    class UserEmailAdmin(admin.TabularInline):
        fields = ('email', 'default')
        extra = 0

class UserPhoneAdmin(admin.TabularInline):
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

class UserAddressAdminInline(admin.StackedInline):
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('default',)+address_fields}),)
    extra = 0
    readonly_fields = ("addr_backend_id",)

@AdminRegisteredTasksView()
@AdminMissivesView()
class UserAdmin(UserAdmin, BaseAdmin):
    change_list_template = "admin/users_change_list.html"
    #formfield_overrides = {PhoneNumberField: {'widget': PhoneNumberPrefixWidget}}
    add_form = UserCreationForm
    form = UserChangeForm
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': get_form_fields()}),)
    readonly_fields = ('method', 'channel', "addr_backend_id", )
    list_display = ('username', 'email', 'phone', 'date_create', 'is_active')

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]['fields'] += ('phone', 'style', 'gender', 'sentry_replay') + address_fields
        self.fieldsets[3][1]['fields'] += ('first_connection',)
        if UserConfig.ForeignKey.optional:
            self.fieldsets[1][1]['fields'] += ('optional',)
        self.add_field(_.informations, ('method', 'channel'))
        if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
            self.fieldsets[1][1]['fields'] += ('nationalities', 'language')
            self.filter_horizontal += ('nationalities',)
        if 'mighty.applications.tenant' in settings.INSTALLED_APPS:
            self.fieldsets[1][1]['fields'] += ('current_tenant',)
            self.raw_id_fields += ('current_tenant',)
        if UserConfig.cgu:
            self.add_field(_.informations, ('cgu',))
        if UserConfig.cgv:
            self.add_field(_.informations, ('cgv',))
        self.raw_id_fields+=UserConfig.ForeignKey.raw_id_fields

    def save_model(self, request, obj, form, change):
        if not change: obj.method = METHOD_BACKEND
        super().save_model(request, obj, form, change)

    def mergeaccounts_view(self, request):
        return self.adminform_view(
            request=request,
            template="admin/merge_accounts.html",
            title="Merge accounts",
            form=UserMergeAccountsAdminForm,
            fields=((None, {'classes': ('wide',), 'fields': ("account_keep", "account_delete"),}),),
            raw_id_fields=("account_keep", "account_delete"),
            log_msg="Merge success",
        )

    def get_urls(self):
        from django.urls import path, include
        urls = super().get_urls()
        my_urls = [
            path("mergeaccounts/",
                self.wrap(self.mergeaccounts_view),
                name=self.get_admin_urlname("mergeaccounts"),
            ),
        ]
        return my_urls + urls
    def save_formset(self, request, form, formset, change):
            instances = formset.save(commit=False)
            for instance in formset.deleted_objects:
                instance.delete()
            for instance in instances:
                instance.save()
            formset.save_m2m()

            super().save_formset(request, form, formset, change)

class TrashmailAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('domain',)}),)
    list_display = ('__str__', 'domain')
    search_fields = ('domain',)

# Draft
class MergeableAccountAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = ((None, {'classes': ('wide',), 'fields': ('primary_user', 'secondary_user', 'reason', 'is_merged')}),)
    list_display = ('__str__', 'is_merged')
    search_fields = ('primary_user', 'secondary_user', 'reason')
    raw_id_fields = ['primary_user', 'secondary_user',]
