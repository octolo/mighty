from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField
from mighty.applications.user import get_form_fields
from mighty.forms import ModelFormDescriptable

allfields = get_form_fields()
required = get_form_fields('required')
optional = get_form_fields('optional')

if 'phone' in allfields:
    class UserCreationForm(UserCreationForm):
        phone = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='FR'), required=False)

if 'password1' not in allfields:
    class UserCreationForm(UserCreationForm):
        password1 = None
        password2 = None

        def clean(self):
            self.cleaned_data["password1"] = None
            super().clean()

class UserCreationForm(UserCreationForm, ModelFormDescriptable):
    class UsernameField(UsernameField):
        pass

    class Meta:
        model = get_user_model()
        fields = allfields

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for field in allfields:
            if field in required:
                self.fields[field].required = True
