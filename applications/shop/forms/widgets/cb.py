from django.forms.widgets import DateInput, TextInput


class CBNumberInput(TextInput):
    input_type = 'cbnumber'
    template_name = 'shop/widgets/number.html'


class CBCVCInput(TextInput):
    input_type = 'cbcvc'
    template_name = 'shop/widgets/cvc.html'


class CBDateInput(DateInput):
    input_type = 'cbdate'
    template_name = 'shop/widgets/date.html'
