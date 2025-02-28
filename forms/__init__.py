
from mighty import translates as _
from mighty.forms.caching import (
    CachingModelChoicesForm as CachingModelChoicesForm,
)
from mighty.forms.caching import (
    CachingModelChoicesFormSet as CachingModelChoicesFormSet,
)
from mighty.forms.descriptors import (
    FormDescriptable,
)
from mighty.forms.descriptors import (
    FormDescriptor as FormDescriptor,
)
from mighty.forms.descriptors import (
    ModelFormDescriptable as ModelFormDescriptable,
)
from mighty.forms.fields import (
    BooleanField as BooleanField,
)
from mighty.forms.fields import (
    CharField,
)
from mighty.forms.fields import (
    ChoiceField as ChoiceField,
)
from mighty.forms.fields import (
    DateField as DateField,
)
from mighty.forms.fields import (
    DateTimeField as DateTimeField,
)
from mighty.forms.fields import (
    DecimalField as DecimalField,
)
from mighty.forms.fields import (
    DurationField as DurationField,
)
from mighty.forms.fields import (
    EmailField as EmailField,
)
from mighty.forms.fields import (
    FileField as FileField,
)
from mighty.forms.fields import (
    FilePathField as FilePathField,
)
from mighty.forms.fields import (
    FloatField as FloatField,
)
from mighty.forms.fields import (
    GenericIPAddressField as GenericIPAddressField,
)
from mighty.forms.fields import (
    ImageField as ImageField,
)
from mighty.forms.fields import (
    IntegerField as IntegerField,
)
from mighty.forms.fields import (
    JSONField as JSONField,
)
from mighty.forms.fields import (
    ModelChoiceField as ModelChoiceField,
)
from mighty.forms.fields import (
    MultipleChoiceField as MultipleChoiceField,
)
from mighty.forms.fields import (
    NullBooleanField as NullBooleanField,
)
from mighty.forms.fields import (
    RegexField as RegexField,
)
from mighty.forms.fields import (
    SlugField as SlugField,
)
from mighty.forms.fields import (
    TimeField as TimeField,
)
from mighty.forms.fields import (
    TypedChoiceField as TypedChoiceField,
)
from mighty.forms.fields import (
    TypedMultipleChoiceField as TypedMultipleChoiceField,
)
from mighty.forms.fields import (
    URLField as URLField,
)
from mighty.forms.fields import (
    UUIDField as UUIDField,
)
from mighty.forms.reporting import ReportingForm as ReportingForm
from mighty.forms.source import SourceForm as SourceForm
from mighty.forms.task import TaskForm as TaskForm
from mighty.forms.timeline import TimelineForm as TimelineForm


class SearchForm(FormDescriptable):
    search = CharField(label=_.search, icon='search')
