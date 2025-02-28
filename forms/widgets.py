
from django.forms.widgets import DateInput, Textarea, TimeInput


class Document(Textarea):
    input_type = 'document'


class Classic(Textarea):
    input_type = 'classic'


class DateInput(DateInput):
    input_type = 'date'


class TimeInput(TimeInput):
    input_type = 'time'


class DateTimeInput(DateInput):
    input_type = 'datetime'


class SignatureInput(Textarea):
    input_type = 'signature'


class InitialsInput(Textarea):
    input_type = 'initials'
