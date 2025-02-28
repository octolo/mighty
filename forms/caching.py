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
                    sample_form.fields[field_name].widget, forms.HiddenInput
                ):
                    if hasattr(self, f'{field_name}_queryset'):
                        sample_form.fields[field_name].queryset = getattr(
                            self, f'{field_name}_queryset'
                        )
                    self.cached_choices[field_name] = list(
                        sample_form.fields[field_name].choices
                    )

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['cached_choices'] = self.cached_choices
        return kwargs


class CachingModelChoicesForm(forms.ModelForm):
    @property
    def model_choice_fields(self):
        return [
            fn
            for fn, f in self.fields.items()
            if isinstance(
                f, forms.ModelChoiceField | forms.ModelMultipleChoiceField
            )
        ]

    def __init__(self, *args, **kwargs):
        cached_choices = kwargs.pop('cached_choices', {})
        super().__init__(*args, **kwargs)
        for field_name, choices in cached_choices.items():
            if choices is not None and field_name in self.fields:
                self.fields[field_name].choices = choices

    def override_value_field(self):
        class ModelForm(forms.ModelForm):
            class Meta:
                model = type(self._obj)
                fields = (self.fieldname,)

        mf = ModelForm()
        self.fields['value'] = mf.fields[self.fieldname]

    def clean(self):
        cleaned_data = super().clean()
        amodel = self._obj.timeline_model(**self.prepared_fields)
        amodel.date_begin = cleaned_data.get('date_begin')
        amodel.date_end = cleaned_data.get('date_end')
        amodel.value = str(cleaned_data.get('value'))
        amodel.save()
