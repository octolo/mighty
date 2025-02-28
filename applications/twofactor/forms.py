import secrets
import string

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from mighty.applications.twofactor import translates as _
from mighty.applications.twofactor import use_twofactor
from mighty.applications.twofactor.apps import TwofactorConfig
from mighty.applications.user.apps import UserConfig
from mighty.applications.user.forms import UserCreationForm
from mighty.forms import FormDescriptable
from mighty.functions import masking_email, masking_phone

UserModel = get_user_model()


class TwoFactorSearchForm(FormDescriptable):
    # A corriger
    # username = forms.CharField(label=_.search, required=True)
    username = forms.CharField(label='Votre email', required=True)  # Need to be fixed
    error_messages = {'invalid_search': _.invalid_search, 'inactive': _.inactive}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_cache = None

    def clean_target(self, target):
        return ''.join(filter(lambda c: c not in string.whitespace, target))

    def Qfilters(self, search):
        return Q(username=search) | Q(**{UserConfig.ForeignKey.email_related_name + '__email': search}) | Q(user_phone__phone=search)

    def get_user_target(self, target):
        target = self.clean_target(target)
        user = UserModel.objects.filter(self.Qfilters(target)).distinct()
        if len(user) == 1: return user[0]
        raise UserModel.DoesNotExist

    def set_session_with_uid(self, uid):
        if self.request: self.request.session['login_uid'] = uid

    def clean(self):
        search = self.cleaned_data.get('username')
        if search:
            try:
                self.user_cache = self.get_user_target(search)
                self.confirm_login_allowed(self.user_cache)
            except UserModel.DoesNotExist:
                raise forms.ValidationError(self.error_messages['invalid_search'], code='invalid_search')
            self.set_session_with_uid(str(self.user_cache.uid))
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(self.error_messages['inactive'], code='inactive')


class TwoFactorChoicesForm(FormDescriptable):
    receiver = forms.CharField(widget=forms.HiddenInput)
    error_messages = {'inactive': _.inactive, 'cant_send': _.cant_send, 'method_not_allowed': _.method_not_allowed}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = self.request.session['login_uid']
        self.user_cache = UserModel.objects.get(uid=self.uid)
        self.emails, self.phones = [], []
        if self.email_authorized: self.get_emails()
        if self.phone_authorized: self.get_phones()

    @property
    def smss(self):
        return self.phones

    @property
    def email_authorized(self):
        return TwofactorConfig.method.email

    @property
    def phone_authorized(self):
        return TwofactorConfig.method.sms

    def get_emails(self):
        if self.user_cache.email: self.emails.append(self.user_cache.email)

    @property
    def emails_masking(self):
        return [masking_email(email) for email in self.emails]

    def get_phones(self):
        if self.user_cache.phone: self.phones.append(self.user_cache.phone)

    @property
    def phones_masking(self):
        return [masking_phone(phone) for phone in self.phones]

    @property
    def basic_authorized(self):
        return TwofactorConfig.method.basic

    def clean(self):
        receiver, status = self.cleaned_data.get('receiver'), False
        if receiver:
            dev, pos = receiver.split('_') if '_' in receiver else (receiver, -1)
            if 'password' in dev:
                status = TwofactorConfig.method.basic
            else:
                receiver = getattr(self, f'{dev}s')[int(pos)]
                status = use_twofactor(receiver)
            if not status:
                raise forms.ValidationError(self.error_messages['cant_send'], code='cant_send')
        return self.cleaned_data


class TwoFactorCodeForm(AuthenticationForm):
    uid = None
    error_messages = {'cant_found': _.cant_found}
    password = forms.fields.CharField(label="Code d'authentification")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_cache = None
        self.fields.pop('username')

    def init_uid(self):
        if self.request.session:
            self.uid = self.request.session.get('login_uid')
        if not self.uid:
            raise forms.ValidationError(self.error_messages['cant_found'], code='cant_found')

    def del_session_with_uid(self):
        del self.request.session['login_uid']

    def clean(self):
        self.init_uid()
        password = self.cleaned_data.get('password')
        if password:
            self.user_cache = authenticate(self.request, username=self.uid, password=password, field_type='uid')
            if self.user_cache is None:
                username_field_verbose_name = getattr(self, 'username_field', 'Username').verbose_name
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': username_field_verbose_name},
                )
            self.del_session_with_uid()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class SignUpForm(UserCreationForm):
    def __init__(self, use_password=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_password = use_password
        if not use_password:
            self.fields.pop('password1')
            self.fields.pop('password2')

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (UserConfig.Field.username, *UserConfig.Field.required)

    def save(self, commit=True):
        if not self.use_password:
            self.cleaned_data['password1'] = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
        return super().save(commit)
