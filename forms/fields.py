from django import forms

from mighty.forms import widgets

self_fields = (
    'icon',
    'dict',
    'isobj',
    'array',
    'many',
    'type',
    'default',
    'fclass',
    'mode',
    'create_if_not_exist',
    'preference',
    'fast_create',
    'form_create',
    'form_edit',
    'field_detail',
    'discriminant',
    'splitted',
    'splitted_refs',
    'vars_url',
    'raw_field',
    'raw_method',
)
options_fields = ('value',)


class MightyFormField(forms.Field):
    api = None

    def __init__(self, **kwargs):
        for field in self_fields:
            setattr(self, field, kwargs.pop(field, False))
        for field in options_fields:
            setattr(self.Options, field, kwargs.pop(field, False))
        super().__init__(**kwargs)

    class Options:
        value = None


class BooleanField(forms.BooleanField, MightyFormField):
    pass


class CharField(forms.CharField, MightyFormField):
    pass


class ChoiceField(forms.ChoiceField, MightyFormField):
    icon = 'check-square'


class TypedChoiceField(forms.TypedChoiceField, MightyFormField):
    icon = 'check-square'


class DateField(forms.DateField, MightyFormField):
    widget = widgets.DateInput
    icon = 'calendar'


class TimeField(forms.TimeField, MightyFormField):
    widget = widgets.TimeInput
    icon = 'calendar'


class DateTimeField(forms.DateTimeField, MightyFormField):
    widget = widgets.DateTimeInput
    icon = 'calendar'


class DecimalField(forms.DecimalField, MightyFormField):
    pass


class DurationField(forms.DurationField, MightyFormField):
    icon = 'hourglass-half'


class EmailField(forms.EmailField, MightyFormField):
    icon = 'at'


class FileField(forms.FileField, MightyFormField):
    icon = 'file-upload'


class FilePathField(forms.FilePathField, MightyFormField):
    icon = 'file'


class FloatField(forms.FloatField, MightyFormField):
    pass


class ImageField(forms.ImageField, MightyFormField):
    icon = 'image'


class IntegerField(forms.IntegerField, MightyFormField):
    pass


class JSONField(forms.JSONField, MightyFormField):
    pass


class GenericIPAddressField(forms.GenericIPAddressField, MightyFormField):
    icon = 'network-wired'


class ModelChoiceField(forms.ModelChoiceField, MightyFormField):
    pass


class MultipleChoiceField(forms.MultipleChoiceField, MightyFormField):
    pass


class TypedMultipleChoiceField(forms.TypedMultipleChoiceField, MightyFormField):
    icon = 'check-square'


class NullBooleanField(forms.NullBooleanField, MightyFormField):
    pass


class RegexField(forms.RegexField, MightyFormField):
    pass


class SlugField(forms.SlugField, MightyFormField):
    icon = 'link'


class TimeField(forms.TimeField, MightyFormField):
    icon = 'clock'


class URLField(forms.URLField, MightyFormField):
    icon = 'link'


class UUIDField(forms.UUIDField, MightyFormField):
    pass
