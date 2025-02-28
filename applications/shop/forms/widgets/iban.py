from django.forms.widgets import TextInput


class IbanInput(TextInput):
    input_type = 'iban'
    template_name = 'shop/widgets/iban.html'


class BicInput(TextInput):
    input_type = 'bic'
    template_name = 'shop/widgets/bic.html'
