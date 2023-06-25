from django import forms

class TimelineForm(forms.ModelForm):
    date_begin = forms.DateField(required=True, widget=forms.SelectDateWidget())
    date_end = forms.DateField(required=False, widget=forms.SelectDateWidget())

    def __init__(self, _obj, fieldname, user, *args, **kwargs):
        self._obj = _obj
        self.fieldname = fieldname
        super().__init__(*args, **kwargs)
        self.override_value_field()
        self.prepared_fields = {
            'object_id': _obj,
            'fmodel': _obj._meta.get_field(fieldname).__class__.__name__,
            'field': fieldname,
            'user': user.username,
        }
