import logging

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.forms.models import BaseInlineFormSet

from mighty import translates as _
from mighty.admin.models import BaseAdmin
from mighty.applications.address import fields as address_fields
from mighty.applications.user import get_form_fields, get_user_phone_model
from mighty.applications.user.apps import UserConfig
from mighty.applications.user.choices import METHOD_BACKEND
from mighty.applications.user.forms import (
    UserChangeForm,
    UserCreationForm,
    UserMergeAccountsAdminForm,
)
from mighty.decorators import AdminRegisteredTasksView

logger = logging.getLogger(__name__)

UserPhoneModel = get_user_phone_model()

if apps.is_installed('allauth'):
    from allauth.account.models import EmailAddress

    class UserEmailAdminFormset(BaseInlineFormSet):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for form in self.forms:
                form.fields['primary'].disabled = True

        def save(self, commit=True):
            instances = super().save(commit=False)
            if commit:
                for instance in instances:
                    if not instance.primary:
                        logger.info(
                            f'UserEmailAdminFormset: save {instance.email}'
                        )
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
            email = self.cleaned_data['email']
            return get_user_model().validate_unique_email(
                email, self.instance.user_id
            )

    class UserEmailAdmin(admin.TabularInline):
        form = UserEmailAdminForm
        extra = 0
        can_delete = True
        fields = ['email', 'verified', 'primary']
        raw_id_fields = ('user',)
        model = EmailAddress  # FIXME: Will be removed when old email models are removed (Messing up with __init__)
        formset = UserEmailAdminFormset

else:

    class UserEmailAdmin(admin.TabularInline):
        fields = ('email', 'default')
        extra = 0


class UserPhoneAdminFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['primary'].disabled = True

    def save(self, commit=True):
        instances = super().save(commit=False)
        if commit:
            for instance in instances:
                if not instance.primary:
                    logger.info(f'UserPhoneAdminFormset: save {instance.phone}')
                    instance.save()
            self.save_m2m()

        return instances


class UserPhoneAdminForm(forms.ModelForm):
    class Meta:
        model = UserPhoneModel
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.primary:
            instance.set_as_primary()
        if commit:
            instance.save()
        return instance

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        return get_user_model().validate_unique_phone(
            phone, self.instance.user_id
        )


class UserPhoneAdmin(admin.TabularInline):
    form = UserPhoneAdminForm
    extra = 0
    can_delete = True
    fields = ['phone', 'verified', 'primary']
    raw_id_fields = ('user',)
    formset = UserPhoneAdminFormset


# FIXME: Django-allauth implementation, need to be moved
from django.core.exceptions import FieldDoesNotExist


def get_user_search_fields():
    ret = []
    User = get_user_model()
    candidates = [
        'username',
        'first_name',
        'last_name',
        'phone',
    ]
    for candidate in candidates:
        try:
            User._meta.get_field(candidate)
            ret.append(candidate)
        except FieldDoesNotExist:
            pass
    return ret


class UserPhoneAdminBase(BaseAdmin):
    view_on_site = False
    list_display = ('phone', 'user', 'primary', 'verified')
    list_filter = ('primary', 'verified')
    search_fields = []
    raw_id_fields = ('user',)
    actions = ['make_verified']
    form = UserPhoneAdminForm

    def get_search_fields(self, request):
        base_fields = get_user_search_fields()
        return ['phone', *['user__' + a for a in base_fields]]

    def make_verified(self, request, queryset):
        queryset.update(verified=True)

    make_verified.short_description = (
        'Mark selected phone addresses as verified'
    )


class InternetProtocolAdmin(admin.TabularInline):
    fields = ('ip',)
    readonly_fields = ('ip',)
    extra = 0


class UserAgentAdmin(admin.TabularInline):
    fields = ('useragent',)
    readonly_fields = ('useragent',)
    extra = 0


class UserAddressAdminInline(admin.StackedInline):
    fieldsets = ((None, {'classes': ('wide',), 'fields': address_fields}),)
    extra = 0
    readonly_fields = ('addr_backend_id',)


@AdminRegisteredTasksView()
class UserAdmin(UserAdmin, BaseAdmin):
    change_list_template = 'admin/users_change_list.html'
    # formfield_overrides = {PhoneNumberField: {'widget': PhoneNumberPrefixWidget}}
    add_form = UserCreationForm
    form = UserChangeForm
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': get_form_fields()}),
    )
    readonly_fields = ('method', 'channel', 'addr_backend_id')
    list_display = (
        'username',
        'email',
        'phone',
        'date_create',
        'is_active',
        'beta_tester',
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]['fields'] += (
            'phone',
            'style',
            'gender',
            'sentry_replay',
            'beta_tester',
            *address_fields,
        )
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
        self.raw_id_fields += UserConfig.ForeignKey.raw_id_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.method = METHOD_BACKEND
        super().save_model(request, obj, form, change)

    def mergeaccounts_view(self, request):
        return self.adminform_view(
            request=request,
            template='admin/merge_accounts.html',
            title='Merge accounts',
            form=UserMergeAccountsAdminForm,
            fields=(
                (
                    None,
                    {
                        'classes': ('wide',),
                        'fields': ('account_keep', 'account_delete'),
                    },
                ),
            ),
            raw_id_fields=('account_keep', 'account_delete'),
            log_msg='Merge success',
        )

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        my_urls = [
            path(
                'mergeaccounts/',
                self.wrap(self.mergeaccounts_view),
                name=self.get_admin_urlname('mergeaccounts'),
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
    fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'primary_user',
                    'secondary_user',
                    'reason',
                    'is_merged',
                ),
            },
        ),
    )
    list_display = ('__str__', 'is_merged')
    search_fields = ('primary_user', 'secondary_user', 'reason')
    raw_id_fields = ['primary_user', 'secondary_user']
