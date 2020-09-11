from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from mighty.applications.user.apps import UserConfig as conf

from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField
class UserCreationForm(UserCreationForm):
    phone = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='CN'))

    class UsernameField(UsernameField):
        pass

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for field in conf.Field.required + (conf.Field.username,):
            self.fields[field].required = True