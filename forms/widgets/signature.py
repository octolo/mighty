from django.forms.widgets import Textarea

class SignatureInput(Textarea):
    input_type = 'signature'
