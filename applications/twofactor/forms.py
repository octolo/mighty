from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.urls import reverse, NoReverseMatch

from mighty.functions import encrypt
from mighty.applications.twofactor import send_sms, send_email, translates as _
from mighty.applications.twofactor.apps import TwofactorConfig

from urllib.parse import quote_plus, unquote_plus
UserModel = get_user_model()

methods = [method for method in TwofactorConfig.methods if hasattr(TwofactorConfig.method, method) and getattr(TwofactorConfig.method, method)]
methods_ws = method = [method for method in TwofactorConfig.methods_ws if hasattr(TwofactorConfig.method, method) and getattr(TwofactorConfig.method, method)]

class UserSearchForm(forms.Form):
    search = forms.CharField(label=_.search, required=True)
    method = forms.CharField(widget=forms.HiddenInput)
    user_cache = None
    method_cache = None
    error_messages = {
        'invalid_search': _.invalid_search,
        'invalid_method': _.invalid_method,
        'inactive': _.inactive,
        'cant_send': _.cant_send,
        'method_not_allowed': _.method_not_allowed,
    }

    def clean(self):
        search = self.cleaned_data.get('search')
        method = self.cleaned_data.get("method")
        if search and method:
            try:
                self.user_cache = UserModel.objects.get(Q(username=search) | Q(email=search) | Q(phone=search))
                self.confirm_login_allowed(self.user_cache)
                self.method_cache = self.cleaned_data.get('method')
                if self.method_cache not in methods:
                    raise forms.ValidationError(self.error_messages['method_not_allowed'], code='method_not_allowed',)
                if self.method_cache in methods_ws:
                    if self.method_cache == 'sms' and self.user_cache.phone is None:
                        raise forms.ValidationError(self.error_messages['cant_send'], code='cant_send',)
                    if self.method_cache == 'email' and self.user_cache.email is None:
                        raise forms.ValidationError(self.error_messages['cant_send'], code='cant_send',)
                    status = send_sms(self.user_cache) if self.method_cache == 'sms' else send_email(self.user_cache)
                    if not status:
                        raise forms.ValidationError(self.error_messages['cant_send'], code='cant_send',)
            except UserModel.DoesNotExist:
                raise forms.ValidationError(self.error_messages['invalid_search'], code='invalid_search',)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(self.error_messages['inactive'], code='inactive', )
            
class TwoFactorForm(AuthenticationForm):
    def __init__(self, uid, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.uid = uid
        self.fields.pop('username')

    def clean(self):
        password = self.cleaned_data.get('password')
        if password:
            self.user_cache = authenticate(self.request, username=self.uid, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

from django.contrib.auth import get_user_model
from mighty.applications.user.apps import UserConfig
from mighty.applications.user.forms import UserCreationForm
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField
class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs): 
        super(SignUpForm, self).__init__(*args, **kwargs) 
        self.fields.pop('password1')
        self.fields.pop('password2')

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (UserConfig.Field.username,) + UserConfig.Field.required

    def save(self, commit=True):
        import secrets, string
        self.cleaned_data["password1"] = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
        user = super(SignUpForm, self).save(commit)
        return user