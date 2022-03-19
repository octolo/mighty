from django.forms.widgets import DateInput
from django.forms import Field

class FormInput(DateInput):
    input_type = 'form'

class SubformField(Field):
    widget = FormInput
    form = None

    def __init__(
        self,
        *,
        form,
        required=True,
        widget=None,
        label=None,
        initial=None,
        help_text="",
        error_messages=None,
        show_hidden_initial=False,
        validators=(),
        localize=False,
        disabled=False,
        label_suffix=None,
    ):
        super().__init__()
        self.form = form

