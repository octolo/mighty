from django import forms

class MightyFormField(forms.Field):
    def __init__(self, **kwargs):
        self.icon = kwargs.pop("icon")
        super().__init__(**kwargs)

class BooleanField(forms.BooleanField, MightyFormField):
    pass

class CharField(forms.CharField, MightyFormField):
    pass

class ChoiceField(forms.ChoiceField, MightyFormField):
    pass

class TypedChoiceField(forms.TypedChoiceField, MightyFormField):
    pass

class DateField(forms.DateField, MightyFormField):
    pass

class DateTimeField(forms.DateTimeField, MightyFormField):
    pass

class DecimalField(forms.DecimalField, MightyFormField):
    pass

class DurationField(forms.DurationField, MightyFormField):
    pass

class EmailField(forms.EmailField, MightyFormField):
    pass

class FileField(forms.FileField, MightyFormField):
    pass

class FilePathField(forms.FilePathField, MightyFormField):
    pass

class FloatField(forms.FloatField, MightyFormField):
    pass

class ImageField(forms.ImageField, MightyFormField):
    pass

class IntegerField(forms.IntegerField, MightyFormField):
    pass

class JSONField(forms.JSONField, MightyFormField):
    pass

class GenericIPAddressField(forms.GenericIPAddressField, MightyFormField):
    pass

class MultipleChoiceField(forms.MultipleChoiceField, MightyFormField):
    pass

class TypedMultipleChoiceField(forms.TypedMultipleChoiceField, MightyFormField):
    pass

class NullBooleanField(forms.NullBooleanField, MightyFormField):
    pass

class RegexField(forms.RegexField, MightyFormField):
    pass

class SlugField(forms.SlugField, MightyFormField):
    pass

class TimeField(forms.TimeField, MightyFormField):
    pass

class URLField(forms.URLField, MightyFormField):
    pass

class UUIDField(forms.UUIDField, MightyFormField):
    pass
