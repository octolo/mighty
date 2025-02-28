from django.forms.widgets import RadioSelect


class PaymentmethodInput(RadioSelect):
    input_type = 'paymentmethodinput'
    template_name = 'shop/widgets/paymentmethod.html'
