from django import forms

class SourceForm(forms.ModelForm):
    date_begin = forms.DateField(required=True, widget=forms.SelectDateWidget())
    date_end = forms.DateField(required=False, widget=forms.SelectDateWidget())

    def __init__(self, _obj, fieldname, user, *args, **kwargs):
        self._obj = _obj
        self.fieldname = fieldname
        super().__init__(*args, **kwargs)
        self.prepared_fields = {
            'model_id': _obj,
            'fmodel': _obj._meta.get_field(fieldname).__class__.__name__,
            'field': fieldname,
            'user': user.username,
        }

    def clean(self):
        cleaned_data = super().clean()
        amodel = self._obj.source_model(**self.prepared_fields)
        amodel.date_begin = cleaned_data.get("date_begin")
        amodel.date_end = cleaned_data.get("date_end")
        amodel.save()
