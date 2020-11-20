from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField

#from mighty.applications.user.apps import UserConfig as conf
from mighty.applications.user import get_form_fields

if 'phone' in get_form_fields():
    class UserCreationForm(UserCreationForm):
        phone = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='FR'))

if 'password' not in get_form_fields():
    class UserCreationForm(UserCreationForm):
        password1 = None
        password2 = None

        def clean_password1(self):
            self.cleaned_data["password2"] = None

        def clean_password2(self):
            self.cleaned_data["password1"] = None

class UserCreationForm(UserCreationForm):
    class UsernameField(UsernameField):
        pass

    class Meta:
        model = get_user_model()
        fields = get_form_fields()

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for field in get_form_fields():
            self.fields[field].required = True


    def clean_password1(self):
        self.cleaned_data["password2"] = None

    def clean_password2(self):
        self.cleaned_data["password1"] = None
    
    def save(self, commit=True):
        self.cleaned_data["password1"] = None
        user = super().save(commit=False)
