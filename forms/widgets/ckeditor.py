
from django.forms.widgets import Textarea

class Document(Textarea):
    input_type = 'document'

class Classic(Textarea):
    input_type = 'classic'
