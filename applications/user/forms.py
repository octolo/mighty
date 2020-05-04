from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from mighty.applications.user.apps import UserConfig

class UserCreationForm(UserCreationForm):
    class UsernameField(UsernameField):
        pass

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        print('tata')
        for field in UserConfig.Field.required + (UserConfig.Field.username,):
            try:
                self.fields[field] = getattr(forms, "%sField" % field.title())(required=True)
            except AttributeError:
                self.fields[field] = forms.CharField(required=True)