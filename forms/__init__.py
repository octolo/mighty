from django import forms
from mighty import translates as _
from mighty.forms.reporting import ReportingForm
from mighty.forms.source import SourceForm
from mighty.forms.timeline import TimelineForm
from mighty.forms.task import TaskForm
from mighty.forms.caching import CachingModelChoicesForm, CachingModelChoicesFormSet
from mighty.forms.descriptors import (
    FormDescriptor,
    FormDescriptable,
    ModelFormDescriptable,
)
from mighty.forms.fields import (
    BooleanField,
    CharField,
    ChoiceField,
    DateField,
    DateTimeField,
    DecimalField,
    DurationField,
    EmailField,
    FileField,
    FilePathField,
    FloatField,
    GenericIPAddressField,
    ImageField,
    IntegerField,
    JSONField,
    MultipleChoiceField,
    NullBooleanField,
    RegexField,
    SlugField,
    TimeField,
    TypedChoiceField,
    TypedMultipleChoiceField,
    URLField,
    UUIDField,
)

class SearchForm(FormDescriptable):
    search = CharField(label=_.search, icon="search")
