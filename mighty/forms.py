from django import forms

"""
Caching query for input choices in FormSet.
In admininline you can set form and formset:
    form = CachingModelChoicesForm
    formset = ResolutionCachingModelChoicesFormSet

You can also add an attribute like model_queryset to override the queryset in "__init__" method:
    def __init__(self, *args, **kwargs):
        self.model_queryset = Model.objects.all()
        super().__init__(*args, **kwargs)
"""
class CachingModelChoicesFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sample_form = self._construct_form(0)
        self.cached_choices = {}
        try:
            model_choice_fields = sample_form.model_choice_fields
        except AttributeError:
            pass
        else:
            for field_name in model_choice_fields:
                if field_name in sample_form.fields and not isinstance(
                    sample_form.fields[field_name].widget, forms.HiddenInput):
                    if hasattr(self, "%s_queryset" % field_name):
                        sample_form.fields[field_name].queryset = getattr(self, "%s_queryset" % field_name)
                    self.cached_choices[field_name] = [c for c in sample_form.fields[field_name].choices]

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["cached_choices"] = self.cached_choices
        return kwargs

class CachingModelChoicesForm(forms.ModelForm):
    @property
    def model_choice_fields(self):
        return [fn for fn, f in self.fields.items() if isinstance(f, (forms.ModelChoiceField, forms.ModelMultipleChoiceField,))]

    def __init__(self, *args, **kwargs):
        cached_choices = kwargs.pop("cached_choices", {})
        super().__init__(*args, **kwargs)
        for field_name, choices in cached_choices.items():
            if choices is not None and field_name in self.fields:
                self.fields[field_name].choices = choices

class HistoryForm(forms.ModelForm):
    value = forms.CharField(required=True)
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
        amodel = self._obj.history_model(**self.prepared_fields)
        amodel.date_begin = cleaned_data.get("date_begin")
        amodel.date_end = cleaned_data.get("date_end")
        amodel.value = bytes(str(cleaned_data.get("value")), 'utf-8')
        amodel.save()

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