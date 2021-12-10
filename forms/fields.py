from django import forms

class MightyFormField(forms.Field):
    icon = None

    def __init__(self, **kwargs):
        self.icon = kwargs.pop("icon") if "icon" in kwargs else self.icon
        super().__init__(**kwargs)

class BooleanField(forms.BooleanField, MightyFormField):
    pass

class CharField(forms.CharField, MightyFormField):
    pass

class ChoiceField(forms.ChoiceField, MightyFormField):
    icon = "check-square"

class TypedChoiceField(forms.TypedChoiceField, MightyFormField):
    icon = "check-square"

class DateField(forms.DateField, MightyFormField):
    icon = "calendar"

class DateTimeField(forms.DateTimeField, MightyFormField):
    icon = "calendar"

class DecimalField(forms.DecimalField, MightyFormField):
    pass

class DurationField(forms.DurationField, MightyFormField):
    icon = "hourglass-half"

class EmailField(forms.EmailField, MightyFormField):
    icon = "at"

class FileField(forms.FileField, MightyFormField):
    icon = "file-upload"

class FilePathField(forms.FilePathField, MightyFormField):
    icon = "file"

class FloatField(forms.FloatField, MightyFormField):
    pass

class ImageField(forms.ImageField, MightyFormField):
    icon = "image"

class IntegerField(forms.IntegerField, MightyFormField):
    pass

class JSONField(forms.JSONField, MightyFormField):
    pass

class GenericIPAddressField(forms.GenericIPAddressField, MightyFormField):
    icon = "network-wired"

class MultipleChoiceField(forms.MultipleChoiceField, MightyFormField):
    pass

class TypedMultipleChoiceField(forms.TypedMultipleChoiceField, MightyFormField):
    icon = "check-square"

class NullBooleanField(forms.NullBooleanField, MightyFormField):
    pass

class RegexField(forms.RegexField, MightyFormField):
    pass

class SlugField(forms.SlugField, MightyFormField):
    icon = "link"

class TimeField(forms.TimeField, MightyFormField):
    icon = "clock"

class URLField(forms.URLField, MightyFormField):
    icon = "link"

class UUIDField(forms.UUIDField, MightyFormField):
    pass
