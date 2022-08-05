
from django.forms.widgets import Textarea, DateInput, TimeInput

#from django.forms import Field
#class SubformField(Field):
#    widget = None
#    form = None
#
#    def __init__(
#        self,
#        *,
#        form,
#        required=True,
#        widget=None,
#        label=None,
#        initial=None,
#        help_text="",
#        error_messages=None,
#        show_hidden_initial=False,
#        validators=(),
#        localize=False,
#        disabled=False,
#        label_suffix=None,
#    ):
#        super().__init__()
#        self.form = form

class Document(Textarea):
    input_type = 'document'

class Classic(Textarea):
    input_type = 'classic'

class SignatureInput(Textarea):
    input_type = 'signature'

class DateInput(DateInput):
    input_type = 'date'

class TimeInput(TimeInput):
    input_type = 'time'

class DateTimeInput(DateInput):
    input_type = 'datetime'